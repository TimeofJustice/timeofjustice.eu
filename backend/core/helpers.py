import json
import logging

from django.conf import settings

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


def default_props(additional_props):
    return {
        "production": settings.DEBUG is False,
        "stable": settings.IS_STABLE,
        **additional_props,
    }
