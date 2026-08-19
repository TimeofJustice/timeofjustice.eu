from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from inertia import render

from core.helpers import BodyContent, default_props, get_or_none
from games import models
from games.decorators import wallet_required
from games.vault import get_vault
from games.views.core.api import get_leaderboard
from games.wallet import clear_wallet, create_wallet, get_wallet, set_wallet

DEFAULT_REDIRECT = "/games/"


def safe_redirect(candidate):
    """Keeps `next` pointing at this site, falling back to the games page."""
    if candidate and candidate.startswith("/") and url_has_allowed_host_and_scheme(candidate, allowed_hosts=None):
        return candidate

    return DEFAULT_REDIRECT


def login(request):
    next_url = safe_redirect(request.GET.get("next"))

    if request.method != "POST":
        if get_wallet(request):
            return HttpResponseRedirect(next_url)

        return render(request, "WalletLoginPage", props=default_props({"error": None, "next": next_url}, request))

    post_data = BodyContent(request)
    next_url = safe_redirect(post_data.get("next"))
    wallet_id = post_data.get("walletId")

    if wallet_id:
        wallet = get_or_none(models.Wallet, wallet_id=wallet_id.lower())

        if wallet:
            set_wallet(request, wallet)
            return HttpResponseRedirect(next_url)

        error_text = "games.login.error.invalid_wallet"
    else:
        error_text = "games.login.error.invalid_request"

    return render(request, "WalletLoginPage", props=default_props({"error": error_text, "next": next_url}, request))


def register(request):
    set_wallet(request, create_wallet())

    return HttpResponseRedirect(safe_redirect(request.GET.get("next")))


def logout(request):
    clear_wallet(request)

    return HttpResponseRedirect("/login/")


@ensure_csrf_cookie
@wallet_required
def index(request):
    wallet = get_wallet(request)

    leaderboard, own_index = get_leaderboard(wallet)
    new_bonus = wallet.refresh_streak() >= 1

    last_visit = timezone.datetime.combine(wallet.last_visit, timezone.datetime.min.time()) if wallet.last_visit else timezone.now()
    next_bonus = last_visit + timezone.timedelta(days=1)

    vault, vault_reset = get_vault()

    page_props = {
        "leaderboard": [wallet.public_json() for wallet in leaderboard[:5]],
        "ownPosition": own_index + 1,
        "newBonus": new_bonus,
        "nextBonus": next_bonus.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dailyBonus": [
            {"day": 1, "reward": 50, "status": "claimed" if wallet.days_played > 0 else "unlocked" if wallet.days_played == 0 else "locked"},
            {"day": 2, "reward": 50, "status": "claimed" if wallet.days_played > 1 else "unlocked" if wallet.days_played == 1 else "locked"},
            {"day": 3, "reward": 100, "status": "claimed" if wallet.days_played > 2 else "unlocked" if wallet.days_played == 2 else "locked"},
            {"day": 4, "reward": 100, "status": "claimed" if wallet.days_played > 3 else "unlocked" if wallet.days_played == 3 else "locked"},
            {"day": 5, "reward": 100, "status": "claimed" if wallet.days_played > 4 else "unlocked" if wallet.days_played == 4 else "locked"},
            {"day": 6, "reward": 200, "status": "unlocked" if wallet.days_played >= 5 else "locked"},
        ],
        "vault": vault.balance,
        "vaultReset": vault_reset.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hintDismissed": wallet.hint_dismissed,
    }

    return render(request, "Games/MainPage", props=default_props(page_props, request))
