from inertia import render

from core.helpers import default_props


def index(request, **kwargs):
    """Page to create a new quiz session or join an existing one."""
    page_props = {
        "navbarSize": "small",
    }

    return render(request, "Quiz/LobbyPage", props=default_props(page_props, request, **kwargs))


def lobby(request, lobby_code, **kwargs):
    page_props = {
        "navbarSize": "small",
    }

    return render(request, "Quiz/SessionPage", props=default_props(page_props, request, **kwargs))
