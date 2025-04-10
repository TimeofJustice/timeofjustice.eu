import uuid

from django.http.response import HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
from inertia import render

from core.helpers import BodyContent, props
from core.models import get_or_none
from .. import models
from ..decorators import wallet_required


@ensure_csrf_cookie
def index(request):
    wallet = request.session.get('wallet_id', None)

    if not wallet:
        return render(request, "Casino/Entry")

    return main(request)


def login(request):
    post_data = BodyContent(request)

    if post_data:
        wallet_id = post_data.get('walletId')
        if wallet_id:
            wallet = get_or_none(models.Wallet, wallet_id=wallet_id.lower())

            if wallet:
                request.session['wallet_id'] = wallet.wallet_id
                return HttpResponseRedirect('/casino/')
            else:
                error_text = "casino.login.error.invalid_wallet"
        else:
            error_text = "casino.login.error.invalid_request"
    else:
        error_text = "casino.login.error.invalid_request"

    page_props = {
        "error": error_text,
    }

    return render(request, "Casino/Login", props=props(page_props))


def register(request):
    wallet_id = uuid.uuid4().hex
    wallet = get_or_none(models.Wallet, wallet_id=wallet_id)

    while wallet:
        wallet_id = uuid.uuid4().hex
        wallet = get_or_none(models.Wallet, wallet_id=wallet_id)

    wallet = models.Wallet.objects.create(wallet_id=wallet_id)

    request.session['wallet_id'] = wallet.wallet_id

    return HttpResponseRedirect('/casino/')


def logout(request):
    response = HttpResponseRedirect('/casino/login/')

    if 'wallet_id' in request.session:
        del request.session['wallet_id']

    return response


@wallet_required
def main(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return HttpResponseRedirect('/casino/login/')

    leaderboard = models.Wallet.objects.order_by('-balance')
    leaderboard = [wallet for wallet in leaderboard]
    own_index = leaderboard.index(wallet)

    page_props = {
        "wallet": wallet.json(),
        "leaderboard": [wallet.public_json() for wallet in leaderboard[:5]],
        "ownPosition": own_index + 1,
    }

    return render(request, "Casino/Main", props=props(page_props))
