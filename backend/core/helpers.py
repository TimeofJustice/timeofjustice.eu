import json

from django.conf import settings


class BodyContent:
    def __init__(self, request):
        body_unicode = request.body.decode('utf-8')

        self.body = None

        try:
            self.body = json.loads(body_unicode)
        except json.JSONDecodeError:
            self.body = {}

    def get(self, key):
        if self.body is None:
            return None

        return self.body.get(key)


def props(props):
    return {
        "production": settings.DEBUG is False,
        "stable": settings.IS_STABLE,
        **props,
    }
