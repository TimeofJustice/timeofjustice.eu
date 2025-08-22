from inertia import render

from core.helpers import default_props


def index(request, **kwargs):
    page_props = {
        "navbarSize": "small",
    }

    return render(request, "Cards/MainPage", props=default_props(page_props, request))