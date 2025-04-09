from django.conf import settings
from inertia import render

from . import models


def props(props):
    return {
        "production": settings.DEBUG is False,
        "stable": settings.IS_STABLE,
        **props
    }


def error(request, status_code):
    page_props = {
        "status_code": status_code
    }

    return render(request, "Error", props=props(page_props))


# Create your views here.
def index(request):
    page_props = {
        'farmItems': {
            'crops': [crop.json() for crop in models.Crop.objects.all()],
            'commodities': [commodity.json() for commodity in models.Commodity.objects.all()]
        }
    }

    return render(request, "FarmingStats", props=props(page_props))