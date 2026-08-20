from functools import wraps
from urllib.parse import quote

from django.http.response import HttpResponseRedirect, JsonResponse

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


def wallet_api_required(view_func):
    """
    Same as `wallet_required`, but for JSON endpoints: a redirect to the login
    page would arrive at the caller as a confusing 200 with HTML in it.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not get_wallet(request):
            return JsonResponse({"error": "games.main.errors.wallet_not_found"}, status=403)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
