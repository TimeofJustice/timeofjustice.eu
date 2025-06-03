from functools import wraps

from django.http.response import HttpResponseRedirect

from games import models
from core.models import get_or_none


def wallet_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        wallet_id = request.session.get('wallet_id')
        if not wallet_id:
            return HttpResponseRedirect('/games/login/')

        wallet = get_or_none(models.Wallet, wallet_id=wallet_id)
        if not wallet:
            del request.session['wallet_id']
            return HttpResponseRedirect('/games/login/')

        return view_func(request, *args, **kwargs)
    return _wrapped_view
