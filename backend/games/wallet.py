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


def reveal_phrase(request, phrase):
    """
    Parks a freshly created phrase in the session so setup can show it once.

    It cannot come from the wallet — only its hash is stored — so this is the
    single copy, and it goes away as soon as setup is saved.
    """
    request.session[REVEAL_KEY] = phrase


def revealable_phrase(request):
    return request.session.get(REVEAL_KEY)


def stop_revealing_phrase(request):
    """Called once setup is saved: the phrase is never shown again."""
    if REVEAL_KEY in request.session:
        del request.session[REVEAL_KEY]


def generate_recovery_phrase():
    return "-".join(secrets.choice(WORDS) for _ in range(WORDS_PER_PHRASE))


def generate_public_id():
    return "".join(secrets.choice(PUBLIC_ID_ALPHABET) for _ in range(PUBLIC_ID_LENGTH))


def hash_recovery_phrase(phrase):
    """
    Keyed hash of a phrase, so the database never holds the phrase itself.

    A plain digest would not be enough: phrases come from a published wordlist,
    so a dump would be brute-forcable offline. The pepper lives in the settings,
    not the database. It is a fast hash on purpose — the phrase carries its own
    entropy, and login stays a single indexed lookup.
    """
    return hmac.new(settings.WALLET_PEPPER.encode(), phrase.encode(), sha256).hexdigest()


def normalise_recovery_phrase(value):
    """Accepts spaces, hyphens and any capitalisation people type or paste."""
    return "-".join(word for word in re.split(r"[^a-zA-Z]+", value) if word).lower()


def find_wallet(identifier):
    """
    Looks a wallet up by its recovery phrase, which is both its identity and
    its only credential.
    """
    if not isinstance(identifier, str):
        return None

    phrase = normalise_recovery_phrase(identifier)

    return get_or_none(models.Wallet, phrase_hash=hash_recovery_phrase(phrase)) if phrase else None


def create_wallet():
    """
    Creates a wallet and returns it together with its recovery phrase.

    The phrase is returned rather than stored: this is the only moment it
    exists in readable form, and the caller has to show it right away.
    """
    public_id = generate_public_id()

    while get_or_none(models.Wallet, pk=public_id):
        public_id = generate_public_id()

    phrase = generate_recovery_phrase()

    while get_or_none(models.Wallet, phrase_hash=hash_recovery_phrase(phrase)):
        phrase = generate_recovery_phrase()

    wallet = models.Wallet.objects.create(
        public_id=public_id,
        phrase_hash=hash_recovery_phrase(phrase),
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
