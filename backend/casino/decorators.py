from functools import wraps

from django.http.response import HttpResponseRedirect

from casino.models import Wallet


def wallet_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        wallet_id = request.session.get('wallet_id')
        if not wallet_id:
            return HttpResponseRedirect('/casino/login/')

        wallet = Wallet.objects.get(wallet_id=wallet_id)
        if not wallet:
            return HttpResponseRedirect('/casino/login/')

        return view_func(request, *args, **kwargs)
    return _wrapped_view
