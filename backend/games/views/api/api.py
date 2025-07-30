from django.http.response import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from core.helpers import BodyContent
from core.models import get_or_none
from games import models
from games.decorators import wallet_required


@wallet_required
@require_http_methods(["POST"])
def update(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return JsonResponse({"error": "games.main.errors.wallet_not_found"}, status=404)

    post_data = BodyContent(request)

    if post_data:
        name = post_data.get('name')

        if name and 3 <= len(name) <= 32 and name.isalnum():
            wallet.name = name
            wallet.save()
        else:
            return JsonResponse({"error": "games.main.errors.name_invalid"}, status=400)
    else:
        return JsonResponse({"error": "games.main.errors.invalid_request"}, status=400)

    return JsonResponse({"name": wallet.name})


@wallet_required
@require_http_methods(["POST"])
def dismiss(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return HttpResponseRedirect('/games/login/')

    wallet.hint_dismissed = True
    wallet.save()

    return JsonResponse({"hintDismissed": wallet.hint_dismissed})


@wallet_required
@require_http_methods(["POST"])
def redeem(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return HttpResponseRedirect('/games/login/')

    if days_since_last_login(wallet) >= 1:
        wallet.days_played += 1
        wallet.last_visit = timezone.now().date()
        reward = 50

        if wallet.days_played == 3 or wallet.days_played == 4:
            reward = 100
        elif wallet.days_played > 4:
            reward = 200

        wallet.balance += reward
        wallet.save()

        last_visit = timezone.datetime.combine(wallet.last_visit, timezone.datetime.min.time()) if wallet.last_visit else timezone.now()
        next_bonus = last_visit + timezone.timedelta(days=1)

        return JsonResponse({"reward": reward, "nextBonus": next_bonus.strftime("%Y-%m-%dT%H:%M:%SZ")})

    return JsonResponse({"error": "games.main.errors.already_claimed"}, status=400)


def days_since_last_login(wallet):
    if wallet.last_visit is None:
        wallet.last_visit = timezone.now().date()
        wallet.save()
    elif (timezone.now().date() - wallet.last_visit).days >= 2:
        wallet.days_played = 0
        wallet.save()

    return (timezone.now().date() - wallet.last_visit).days


def get_leaderboard(wallet):
    leaderboard = models.Wallet.objects.order_by('-balance')
    leaderboard = list(leaderboard)
    own_index = leaderboard.index(wallet)

    return leaderboard, own_index


@wallet_required
def leaderboard(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return HttpResponseRedirect('/games/login/')

    leaderboard, own_index = get_leaderboard(wallet)

    return JsonResponse({
        "leaderboard": [wallet.public_json() for wallet in leaderboard[:5]],
        "ownPosition": own_index + 1,
    })


def get_vault():
    vault = get_or_none(models.Vault, id=1)

    if not vault:
        vault = models.Vault.objects.create(id=1, last_redemption=timezone.now().date())

    vault_reset = timezone.datetime.combine(vault.last_redemption, timezone.datetime.min.time()) if vault.last_redemption else timezone.now()
    vault_reset = timezone.make_aware(vault_reset) if timezone.is_naive(vault_reset) else vault_reset
    vault_reset = vault_reset + timezone.timedelta(days=1)

    if vault_reset < timezone.now():
        vault.balance = 0
        vault.last_redemption = timezone.now().date()
        vault.save()

    return vault, vault_reset


@wallet_required
def vault(request):
    vault, vault_reset = get_vault()

    return JsonResponse({
        "vault": vault.balance,
        "vaultReset": vault_reset.strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
