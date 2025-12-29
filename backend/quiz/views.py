from inertia import render

from core.helpers import default_props


def index(request, **kwargs):
    page_props = {
    }

    return render(request, "Quiz/LobbyPage", props=default_props(page_props, request, **kwargs))
