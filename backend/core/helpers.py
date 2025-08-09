import json
import logging

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
    return {
        "production": settings.DEBUG is False,
        "stable": settings.IS_STABLE,
        "offcanvasComponent": offcanvas_component,
        "offcanvasProps": kwargs,
        "offcanvasSource": request.headers.get("X-Offcanvas-Source"),
        **additional_props,
    }


def call_view_by_url(url, request, error_callback, offcanvas_component=None, *args, **kwargs):
    try:
        if url.startswith("http://") or url.startswith("https://"):
            from urllib.parse import urlparse
            url = urlparse(url).path

        match = resolve(url)
        view_func = match.func

        return view_func(request, offcanvas_component, **kwargs)

    except Resolver404:
        return error_callback(request, 404)
