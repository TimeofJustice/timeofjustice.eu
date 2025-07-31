from inertia import render

from core.helpers import props

from . import models


def error(request, status_code):
    page_props = {
        "status_code": status_code,
    }

    return render(request, "Error", props=props(page_props))


# Create your views here.
def index(request):
    page_props = {
        'farmItems': {
            'crops': [crop.json() for crop in models.Crop.objects.all()],
            'commodities': [commodity.json() for commodity in models.Commodity.objects.all()],
        },
    }

    return render(request, "FarmingStats", props=props(page_props))
