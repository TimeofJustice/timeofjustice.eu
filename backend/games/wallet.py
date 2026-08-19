import uuid

from django.utils import timezone

from core.helpers import get_or_none
from games import models
from games.vault import get_vault

SESSION_KEY = "wallet_id"


def get_wallet_by_session(session):
    """
    The wallet a session belongs to, or None. Takes the session rather than a
    request, so websocket consumers can use it too.
    """
    wallet_id = session.get(SESSION_KEY)

    if not wallet_id:
        return None

    return get_or_none(models.Wallet, wallet_id=wallet_id)


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
    request.session[SESSION_KEY] = wallet.wallet_id
    request.wallet = wallet

    return wallet


def clear_wallet(request):
    """Logs the current wallet out."""
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]

    request.wallet = None


def create_wallet():
    """Creates a new wallet with a collision-free id."""
    wallet_id = uuid.uuid4().hex

    while get_or_none(models.Wallet, wallet_id=wallet_id):
        wallet_id = uuid.uuid4().hex

    return models.Wallet.objects.create(wallet_id=wallet_id, last_visit=timezone.now().date())


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
