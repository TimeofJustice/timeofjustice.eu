from functools import wraps

from django.http.response import HttpResponseRedirect


def wallet_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        wallet = request.session.get('wallet_id')
        if not wallet:
            return HttpResponseRedirect('/casino/login/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
