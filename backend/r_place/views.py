import django.shortcuts
from django.http import JsonResponse
from inertia import render

from core.helpers import props
from .models import Cell


def index(request):
    page_props = {
    }

    return render(request, "RPlace", props=props(page_props))


def load_chunk(request, x, y, size=100):
    cells = Cell.objects.filter(
        x__gte=x, x__lt=x + size,
        y__gte=y, y__lt=y + size
    ).values("x", "y", "color")

    cells = list(cells)

    return JsonResponse({"cells": cells})
