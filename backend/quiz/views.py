from inertia import render

from core.helpers import default_props


def index(request, **kwargs):
    page_props = {
    }

    return render(request, "Quiz/SessionPage", props=default_props(page_props, request, **kwargs))


def lobby(request, lobby_code, **kwargs):
    page_props = {
    }

    return render(request, "Quiz/SessionPage", props=default_props(page_props, request, **kwargs))
