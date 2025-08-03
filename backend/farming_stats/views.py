from inertia import render

from core.helpers import default_props
from farming_stats import models


def index(request):
    page_props = {
        'farmItems': {
            'crops': [crop.json() for crop in models.Crop.objects.all()],
            'commodities': [commodity.json() for commodity in models.Commodity.objects.all()],
        },
    }

    return render(request, "FarmingStats", props=default_props(page_props))
