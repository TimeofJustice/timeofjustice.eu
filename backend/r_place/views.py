from django.http import JsonResponse
from django.shortcuts import redirect
from inertia import render

from core.helpers import default_props
from r_place.models import Canvas, Cell, RenderedCanvas


def index(request, canvas=None):
    selected_canvas = (
        Canvas.objects.filter(active=True).first()
        if canvas is None
        else Canvas.objects.filter(name=canvas).first()
    )

    if not selected_canvas:
        return redirect("/")

    page_props = {
        "activeCanvas": {
            "name": selected_canvas.name,
            "width": selected_canvas.width,
            "height": selected_canvas.height,
            "active": selected_canvas.active,
        },
        "canvases": list(Canvas.objects.all().values("name", "width", "height", "active")),
        "navbarSize": "small",
    }

    return render(request, "RPlace", props=default_props(page_props, request))


def load_canvas(request, canvas):
    rendered_canvas = RenderedCanvas.objects.filter(
        canvas__name=canvas,
    ).order_by("-created_at").first()

    if rendered_canvas:
        cells = Cell.objects.filter(
            last_modified__gt=rendered_canvas.created_at,
            canvas__name=rendered_canvas.canvas.name,
        ).values("x", "y", "color")

        return JsonResponse(
            {
                "image": f"/files/images/r-place/{rendered_canvas.image_name}" if rendered_canvas else None,
                "cells": list(cells),
            },
        )
    cells = Cell.objects.filter(
        canvas__name=canvas,
    ).values("x", "y", "color")

    return JsonResponse(
        {
            "image": None,
            "cells": list(cells),
        },
    )
