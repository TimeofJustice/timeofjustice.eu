from django.shortcuts import redirect
from django.http import JsonResponse
from inertia import render

from core.helpers import props
from .models import Cell, Canvas


def index(request, canvas=None):
    if canvas is None:
        selected_canvas = Canvas.objects.filter(active=True).first()
    else:
        selected_canvas = Canvas.objects.filter(name=canvas).first()

    if not selected_canvas:
        return redirect("/")

    page_props = {
        "activeCanvas": {
            "name": selected_canvas.name,
            "width": selected_canvas.width,
            "height": selected_canvas.height,
            "active": selected_canvas.active
        },
        "canvases": list(Canvas.objects.all().values("name", "width", "height", "active")),
    }

    return render(request, "RPlace", props=props(page_props))


def load_chunk(request, x, y, canvas, size=100):
    cells = Cell.objects.filter(
        x__gte=x, x__lt=x + size,
        y__gte=y, y__lt=y + size,
        canvas__name=canvas
    ).values("x", "y", "color")

    cells = list(cells)

    return JsonResponse({"cells": cells})
