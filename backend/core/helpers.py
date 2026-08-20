import json
import logging
from urllib.parse import urlparse

from django.conf import settings
from django.urls import Resolver404, resolve

logger = logging.getLogger(__name__)


class BodyContent:
    def __init__(self, request):
        body_unicode = request.body.decode("utf-8")

        self.body = None

        try:
            self.body = json.loads(body_unicode)
        except json.JSONDecodeError as e:
            self.body = {}
            logger.warning(f"Invalid JSON body in request. Error: {e}")

    def get(self, key, default=None):
        if self.body is None:
            return default

        return self.body.get(key, default)


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def default_props(additional_props, request, offcanvas_component=None, **kwargs):
    # Imported here because games.wallet imports this module for get_or_none.
    from games.wallet import get_wallet, phrase_is_pending

    wallet = get_wallet(request)
    wallet_props = None

    if wallet:
        # `mustSavePhrase` opens the settings by itself, so a phrase issued on
        # sign-in cannot be missed even by a wallet that is otherwise set up.
        wallet_props = wallet.json() | {"mustSavePhrase": phrase_is_pending(request)}

    offcanvas_state = (
        {
            "source": request.headers.get("X-Offcanvas-Source"),
            "target": request.headers.get("X-Offcanvas-Target", request.headers.get("X-Offcanvas-Source")),
            "component": offcanvas_component,
            "props": kwargs,
        }
        if offcanvas_component
        else None
    )

    return {
        "production": settings.DEBUG is False,
        "stable": settings.IS_STABLE,
        "offcanvasState": offcanvas_state,
        # Shared on every page so the navbar can show the wallet site-wide.
        "wallet": wallet_props,
        **additional_props,
    }


def call_view_by_url(url, request, error_callback, offcanvas_component=None, **kwargs):
    try:
        if url.startswith(("http://", "https://")):
            url = urlparse(url).path

        match = resolve(url)
        view_func = match.func
        all_kwargs = {**kwargs, **match.kwargs}

        return view_func(request, offcanvas_component=offcanvas_component, **all_kwargs)

    except Resolver404:
        return error_callback(request, 404)
