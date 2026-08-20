import hmac
import re
import secrets
from hashlib import sha256

from django.conf import settings
from django.utils import timezone

from core.helpers import get_or_none
from games import models
from games.vault import get_vault
from games.wordlist import WORDS, WORDS_PER_PHRASE

SESSION_KEY = "wallet"

# Crockford base32: no I, L, O or U, so a public id cannot be misread aloud.
PUBLIC_ID_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
PUBLIC_ID_LENGTH = 6

# The 32 character hex ids wallets used before wallet phrases existed.
LEGACY_ID_PATTERN = re.compile(r"[0-9a-f]{32}", re.IGNORECASE)

# Set when a wallet is created, so its phrase can be shown exactly once.
REVEAL_KEY = "reveal_phrase"


def get_wallet_by_session(session):
    """
    The wallet a session belongs to, or None. Takes the session rather than a
    request, so websocket consumers can use it too.
    """
    phrase = session.get(SESSION_KEY)

    if not phrase:
        return None

    return get_or_none(models.Wallet, pk=phrase)


def get_wallet(request):
    """
    The wallet of the current session, or None when there is none (or it no
    longer exists, in which case the stale session entry is dropped).

    The result is cached on the request, so views behind `wallet_required` can
    call this freely without hitting the database again.
    """
    cached = getattr(request, "wallet", None)
    if cached is not None:
        return cached

    wallet = get_wallet_by_session(request.session)

    if not wallet:
        clear_wallet(request)
        return None

    request.wallet = wallet

    return wallet


def set_wallet(request, wallet):
    """Logs the given wallet in for this session."""
    # A fresh session key on sign-in, so a cookie planted beforehand cannot be
    # reused to ride along on the wallet.
    request.session.cycle_key()
    request.session[SESSION_KEY] = wallet.pk
    request.wallet = wallet

    return wallet


def clear_wallet(request):
    """Logs the current wallet out."""
    for key in (SESSION_KEY, REVEAL_KEY):
        if key in request.session:
            del request.session[key]

    request.wallet = None


def reveal_phrase(request, phrase, reason="registered"):
    """
    Parks a freshly issued phrase in the session so setup can show it once.

    It cannot come from the wallet, where only its hash is stored, so this is the
    single copy, and it goes away as soon as setup is saved. `reason` tells the
    frontend whether to introduce the phrase or to warn that the old id is now
    spent.
    """
    request.session[REVEAL_KEY] = {"phrase": phrase, "reason": reason}


def revealable_phrase(request):
    return request.session.get(REVEAL_KEY) or {}


def phrase_is_pending(request):
    """Whether the owner still has an unsaved phrase in front of them."""
    return bool(revealable_phrase(request))


def stop_revealing_phrase(request):
    """Called once setup is saved: the phrase is never shown again."""
    if REVEAL_KEY in request.session:
        del request.session[REVEAL_KEY]


def generate_wallet_phrase():
    return "-".join(secrets.choice(WORDS) for _ in range(WORDS_PER_PHRASE))


def generate_public_id():
    return "".join(secrets.choice(PUBLIC_ID_ALPHABET) for _ in range(PUBLIC_ID_LENGTH))


def hash_wallet_phrase(phrase):
    """
    Keyed hash of a phrase, so the database never holds the phrase itself.

    A plain digest would not be enough: phrases come from a published wordlist,
    so a dump would be brute-forcable offline. The pepper lives in the settings,
    not the database. It is a fast hash on purpose: the phrase carries its own
    entropy, and login stays a single indexed lookup.
    """
    return hmac.new(settings.WALLET_PEPPER.encode(), phrase.encode(), sha256).hexdigest()


def normalise_wallet_phrase(value):
    """Accepts spaces, hyphens and any capitalisation people type or paste."""
    return "-".join(word for word in re.split(r"[^a-zA-Z]+", value) if word).lower()


def hash_legacy_id(wallet_id):
    """Keyed the same way as a phrase, so no old id sits readable in the table."""
    return hmac.new(settings.WALLET_PEPPER.encode(), wallet_id.lower().encode(), sha256).hexdigest()


def find_legacy_wallet(identifier):
    """
    Matches one of the old hex ids, which still open a wallet exactly once.

    Kept because the site spent its whole life telling people to save that id,
    and phrases only arrived later.
    """
    if not isinstance(identifier, str):
        return None

    candidate = identifier.strip()

    if not LEGACY_ID_PATTERN.fullmatch(candidate):
        return None

    return get_or_none(models.Wallet, legacy_id_hash=hash_legacy_id(candidate))


def assign_wallet_phrase(wallet):
    """
    Gives an existing wallet a new phrase and returns it.

    Whatever phrase it had stops working, and the returned one is the only
    readable copy, so the caller has to put it in front of somebody.
    """
    phrase = generate_wallet_phrase()

    while get_or_none(models.Wallet, phrase_hash=hash_wallet_phrase(phrase)):
        phrase = generate_wallet_phrase()

    wallet.phrase_hash = hash_wallet_phrase(phrase)
    wallet.save(update_fields=["phrase_hash"])

    return phrase


def upgrade_legacy_wallet(wallet):
    """Issues a phrase to a wallet arriving on its old id, and burns that id."""
    phrase = assign_wallet_phrase(wallet)

    wallet.legacy_id_hash = None
    wallet.save(update_fields=["legacy_id_hash"])

    return phrase


def find_wallet(identifier):
    """
    Looks a wallet up by its wallet phrase, which is both its identity and
    its only credential.
    """
    if not isinstance(identifier, str):
        return None

    phrase = normalise_wallet_phrase(identifier)

    return get_or_none(models.Wallet, phrase_hash=hash_wallet_phrase(phrase)) if phrase else None


def create_wallet():
    """
    Creates a wallet and returns it together with its wallet phrase.

    The phrase is returned rather than stored: this is the only moment it
    exists in readable form, and the caller has to show it right away.
    """
    public_id = generate_public_id()

    while get_or_none(models.Wallet, pk=public_id):
        public_id = generate_public_id()

    phrase = generate_wallet_phrase()

    while get_or_none(models.Wallet, phrase_hash=hash_wallet_phrase(phrase)):
        phrase = generate_wallet_phrase()

    wallet = models.Wallet.objects.create(
        public_id=public_id,
        phrase_hash=hash_wallet_phrase(phrase),
        last_visit=timezone.now().date(),
    )

    return wallet, phrase


def update_balance(wallet, amount):
    """
    Moves `amount` tokens into the wallet and the same amount out of the vault
    (negative `amount` for a bet, positive for a payout).
    """
    wallet.balance += amount
    wallet.save()

    vault, _ = get_vault()
    vault.balance -= amount
    vault.save()
