from django.conf import settings
from django.http.response import HttpResponseRedirect
from inertia import render

from .. import models
from ..decorators import wallet_required


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


def index(request):
    wallet = request.session.get('wallet_id', None)

    if not wallet:
        return render(request, "Casino/Entry")

    return wallet_test(request)


def login(request, error=None):
    page_props = {
        "error": error,
    }

    return render(request, "Casino/Login", props=props(page_props))


def register(request):
    response = HttpResponseRedirect('/casino/')

    request.session['wallet_id'] = 'cookie_value'

    return response


@wallet_required
def wallet_test(request):
    page_props = {
        "wallet": request.session['wallet_id'],
    }

    return render(request, "Casino/Main", props=props(page_props))
