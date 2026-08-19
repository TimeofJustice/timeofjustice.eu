from functools import wraps
from urllib.parse import quote

from django.http.response import HttpResponseRedirect

from games.wallet import get_wallet


def wallet_required(view_func):
    """
    Sends requests without a valid wallet to the login page and caches the
    wallet on the request, so the view can just call `get_wallet(request)`.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not get_wallet(request):
            return HttpResponseRedirect(f"/login/?next={quote(request.get_full_path())}")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
