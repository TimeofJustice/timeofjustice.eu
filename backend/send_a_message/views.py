from inertia import render

from core.helpers import call_view_by_url, default_props, get_or_none

def index(request, **kwargs):
    page_props = {

    }

    return render(request, "SendAMessagePage", props=default_props(page_props, request, **kwargs))
