"""Replaces the hex wallet id with a public id, and stores only a keyed hash of
the recovery phrase.

Written by hand and kept as one step, because a primary key swap has no valid
intermediate state for the autodetector — and because the r/place foreign key
has to be carried across in the same breath.

Existing wallets keep their old hex id as a one-shot credential: it is hashed
into `legacy_id_hash`, and the first sign-in that uses it issues a phrase and
clears it. They are also given a phrase here, printed once, as a fallback for
whoever runs the deploy — after this the plaintext is gone either way.
"""

import hmac
import secrets
from hashlib import sha256

from django.conf import settings
from django.db import migrations, models

from games.wordlist import WORDS, WORDS_PER_PHRASE

PUBLIC_ID_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
PUBLIC_ID_LENGTH = 6


def issue_credentials(apps, schema_editor):
    wallet_model = apps.get_model("games", "Wallet")

    public_ids = set()
    issued = []

    for wallet in wallet_model.objects.all():
        public_id = "".join(secrets.choice(PUBLIC_ID_ALPHABET) for _ in range(PUBLIC_ID_LENGTH))

        while public_id in public_ids:
            public_id = "".join(secrets.choice(PUBLIC_ID_ALPHABET) for _ in range(PUBLIC_ID_LENGTH))

        public_ids.add(public_id)

        phrase = "-".join(secrets.choice(WORDS) for _ in range(WORDS_PER_PHRASE))

        wallet.public_id = public_id
        wallet.phrase_hash = hmac.new(settings.WALLET_PEPPER.encode(), phrase.encode(), sha256).hexdigest()
        # The id everyone was told to save still works, once.
        wallet.legacy_id_hash = hmac.new(settings.WALLET_PEPPER.encode(), wallet.wallet_id.lower().encode(), sha256).hexdigest()
        wallet.save(update_fields=["public_id", "phrase_hash", "legacy_id_hash"])

        issued.append((public_id, wallet.name, phrase))

    if issued:
        # The one and only chance to see these. Wallets that existed before this
        # migration have no other way back in.
        print("\nPhrases issued to existing wallets. Their old ids also still work, once:")
        for public_id, name, phrase in issued:
            print(f"  {public_id}  {name:<20} {phrase}")
        print()


SWAP_KEY = """
ALTER TABLE games_wallet ALTER COLUMN public_id SET NOT NULL;
ALTER TABLE games_wallet ALTER COLUMN phrase_hash SET NOT NULL;

-- carry the cells over to the new key before the old one disappears
ALTER TABLE r_place_cell ADD COLUMN wallet_public_id varchar(6);

UPDATE r_place_cell AS c
   SET wallet_public_id = w.public_id
  FROM games_wallet AS w
 WHERE c.wallet_id = w.wallet_id;

DO $$
DECLARE
    constraint_name text;
BEGIN
    SELECT conname INTO constraint_name
      FROM pg_constraint
     WHERE conrelid = 'r_place_cell'::regclass
       AND contype = 'f'
       AND confrelid = 'games_wallet'::regclass;

    IF constraint_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE r_place_cell DROP CONSTRAINT %I', constraint_name);
    END IF;

    SELECT conname INTO constraint_name
      FROM pg_constraint
     WHERE conrelid = 'games_wallet'::regclass AND contype = 'p';

    IF constraint_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE games_wallet DROP CONSTRAINT %I', constraint_name);
    END IF;
END $$;

ALTER TABLE r_place_cell DROP COLUMN wallet_id;
ALTER TABLE r_place_cell RENAME COLUMN wallet_public_id TO wallet_id;

ALTER TABLE games_wallet ADD PRIMARY KEY (public_id);
ALTER TABLE games_wallet DROP COLUMN wallet_id;
ALTER TABLE games_wallet ADD CONSTRAINT games_wallet_phrase_hash_key UNIQUE (phrase_hash);

ALTER TABLE r_place_cell
    ADD CONSTRAINT r_place_cell_wallet_id_fk_games_wallet_public_id
    FOREIGN KEY (wallet_id) REFERENCES games_wallet (public_id) DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX r_place_cell_wallet_id_idx ON r_place_cell (wallet_id);
"""


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0014_avatar_wallet_avatar"),
        ("r_place", "0009_alter_canvas_options_cell_wallet"),
    ]

    operations = [
        migrations.AddField(
            model_name="wallet",
            name="public_id",
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AddField(
            model_name="wallet",
            name="phrase_hash",
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="wallet",
            name="legacy_id_hash",
            field=models.CharField(blank=True, editable=False, max_length=64, null=True, unique=True),
        ),
        migrations.RunPython(issue_credentials, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunSQL(SWAP_KEY, migrations.RunSQL.noop)],
            state_operations=[
                migrations.RemoveField(model_name="wallet", name="wallet_id"),
                migrations.AlterField(
                    model_name="wallet",
                    name="public_id",
                    field=models.CharField(editable=False, max_length=6, primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="wallet",
                    name="phrase_hash",
                    field=models.CharField(editable=False, max_length=64, unique=True),
                ),
            ],
        ),
    ]
