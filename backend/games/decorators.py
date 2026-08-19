from functools import wraps

from django.http.response import HttpResponseRedirect

from games.wallet import get_wallet


def wallet_required(view_func):
    """
    Rejects requests without a valid wallet and caches the wallet on the
    request, so the view can just call `get_wallet(request)`.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not get_wallet(request):
            return HttpResponseRedirect("/games/login/")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
