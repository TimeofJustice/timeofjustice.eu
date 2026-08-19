from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from inertia import render

from core.helpers import BodyContent, default_props, get_or_none
from games import models
from games.decorators import wallet_required
from games.vault import get_vault
from games.views.core.api import get_leaderboard
from games.wallet import clear_wallet, create_wallet, get_wallet, set_wallet


@ensure_csrf_cookie
def index(request):
    if not get_wallet(request):
        return render(request, "Games/EntryPage", props=default_props({}, request))

    return main(request)


def login(request):
    post_data = BodyContent(request)

    if post_data:
        wallet_id = post_data.get("walletId")
        if wallet_id:
            wallet = get_or_none(models.Wallet, wallet_id=wallet_id.lower())

            if wallet:
                set_wallet(request, wallet)
                return HttpResponseRedirect("/games/")
            error_text = "games.login.error.invalid_wallet"
        else:
            error_text = "games.login.error.invalid_request"
    else:
        error_text = "games.login.error.invalid_request"

    page_props = {
        "error": error_text,
    }

    return render(request, "Games/LoginPage", props=default_props(page_props, request))


def register(request):
    set_wallet(request, create_wallet())

    return HttpResponseRedirect("/games/")


def logout(request):
    clear_wallet(request)

    return HttpResponseRedirect("/games/login/")


@wallet_required
def main(request):
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
