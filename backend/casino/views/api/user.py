from django.http.response import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods

from casino import models
from casino.decorators import wallet_required
from core.helpers import BodyContent
from core.models import get_or_none
from django.utils import timezone


@wallet_required
@require_http_methods(["POST"])
def update(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return JsonResponse({"error": "casino.main.errors.wallet_not_found"}, status=404)

    post_data = BodyContent(request)

    if post_data:
        name = post_data.get('name')

        if name and 3 <= len(name) <= 32 and name.isalnum():
            wallet.name = name
            wallet.save()
        else:
            return JsonResponse({"error": "casino.main.errors.name_invalid"}, status=400)
    else:
        return JsonResponse({"error": "casino.main.errors.invalid_request"}, status=400)

    return JsonResponse({"name": wallet.name})


@wallet_required
@require_http_methods(["POST"])
def redeem(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return HttpResponseRedirect('/casino/login/')

    if days_since_last_login(wallet) >= 1:
        wallet.days_played += 1
        wallet.last_visit = timezone.now().date()
        reward = 50

        if wallet.days_played == 3:
            reward = 100
        elif wallet.days_played == 4:
            reward = 100
        elif wallet.days_played > 4:
            reward = 200

        wallet.balance += reward
        wallet.save()

        return JsonResponse({"reward": reward})

    return JsonResponse({"error": "casino.main.errors.already_claimed"}, status=400)


def days_since_last_login(wallet):
    if wallet.last_visit is None:
        wallet.last_visit = timezone.now().date()
        wallet.save()
    elif 2 <= (timezone.now().date() - wallet.last_visit).days:
        wallet.days_played = 0
        wallet.save()

    return (timezone.now().date() - wallet.last_visit).days


@wallet_required
def leaderboard(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    leaderboard = models.Wallet.objects.order_by('-balance')
    leaderboard = [wallet for wallet in leaderboard]
    own_index = leaderboard.index(wallet)

    return JsonResponse({
        "leaderboard": [wallet.public_json() for wallet in leaderboard[:5]],
        "ownPosition": own_index + 1,
    })
