import json
import uuid

from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
from inertia import render

from core.models import get_or_none
from .. import models
from ..decorators import wallet_required


class BodyContent:
    def __init__(self, request):
        body_unicode = request.body.decode('utf-8')

        self.body = None

        try:
            self.body = json.loads(body_unicode)
        except:
            pass

    def get(self, key):
        if self.body is None:
            return None

        return self.body.get(key)


def props(props):
    return {
        "production": settings.DEBUG is False,
        **props
    }


def error(request, status_code):
    page_props = {
        "status_code": status_code
    }

    return render(request, "Error", props=props(page_props))


@ensure_csrf_cookie
def index(request):
    wallet = request.session.get('wallet_id', None)

    if not wallet:
        return render(request, "Casino/Entry")

    return main(request)


@ensure_csrf_cookie
def login(request):
    post_data = BodyContent(request)
    error = None

    if post_data:
        wallet_id = post_data.get('wallet_id')
        if wallet_id:
            wallet = get_or_none(models.Wallet, wallet_id=wallet_id.lower())

            if wallet:
                request.session['wallet_id'] = wallet.wallet_id
                return HttpResponseRedirect('/casino/')
            else:
                error = "casino.login.error.invalid_wallet"

    page_props = {
        "error": error,
    }

    return render(request, "Casino/Login", props=props(page_props))


def register(request):
    response = HttpResponseRedirect('/casino/')

    wallet_id = uuid.uuid4().hex
    wallet = get_or_none(models.Wallet, wallet_id=wallet_id)

    while wallet:
        wallet_id = uuid.uuid4().hex
        wallet = get_or_none(models.Wallet, wallet_id=wallet_id)

    wallet = models.Wallet.objects.create(wallet_id=wallet_id)

    request.session['wallet_id'] = wallet.wallet_id

    return response


def logout(request):
    response = HttpResponseRedirect('/casino/login/')

    if 'wallet_id' in request.session:
        del request.session['wallet_id']

    return response


def wallet_to_leaderboard(wallet):
    return {
        "name": wallet.name,
        "balance": wallet.balance,
    }


@wallet_required
def main(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    page_props = {
        "wallet": wallet.json(),
        "leaderboard": [wallet_to_leaderboard(wallet) for wallet in models.Wallet.objects.order_by('-balance')[:5]],
        "your_position": models.Wallet.objects.filter(balance__gt=wallet.balance).count() + 1,
    }

    return render(request, "Casino/Main", props=props(page_props))
