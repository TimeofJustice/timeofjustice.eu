import json
import os
from django.conf import settings
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from . import models


def get_json():
    json_projects = []
    projects = models.Project.objects.all()

    for project in projects:
        serialized_obj = model_to_dict(project)

        serialized_obj["status_id"] = project.status.id
        serialized_obj["status"] = project.status.name

        serialized_obj["languages"] = []

        for language in project.languages.all():
            serialized_obj["languages"].append(language.name)

        serialized_obj["images"] = []

        for image in project.image_set.all():
            image_elements = image.image.url.split("/")[6::]
            preview_elements = image.preview.url.split("/")[6::]
            serialized_obj["images"].append([["/".join(image_elements), "/".join(preview_elements)], image.alt])

        json_projects.append(serialized_obj)

    json_projects = sorted(json_projects, key=lambda k: k["status_id"])
    json_projects.reverse()

    return json_projects


def project(request, project_id):
    projects = get_json()

    if len(projects) < project_id:
        return JsonResponse({"error": "Project not found."}, status=404)

    return JsonResponse(projects[project_id], safe=False)


def projects_list(request):
    projects = get_json()

    return JsonResponse(projects, safe=False)


def index(request):
    context = {
        "mode": "dark"
    }

    if request.COOKIES.get("mode") is not None:
        context["mode"] = request.COOKIES.get("mode")

    response = render(request, "index.html", context)
    return response


def handler404(request, *args, **kwargs):
    return HttpResponseRedirect('/')


def robot(request):
    lines = [
        "User-agent: *",
        "Disallow: /api/",
        "Disallow: /admin/",
        "Allow: /"
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")


def get_cells():
    cells = models.Cell.objects.all()
    print(cells)

    cells_list = {}

    for cell in cells:
        if cell.x not in cells_list.keys():
            cells_list.update({cell.x: {}})

        cells_list[cell.x].update({cell.y: cell.color})

    return cells_list


def place_get(request):
    return JsonResponse(get_cells(), safe=False)


def place_set(request):
    # Get the color
    color = request.GET.get("color")
    x = request.GET.get("x")
    y = request.GET.get("y")

    # check if cell exists
    cell = models.Cell.objects.filter(x=x, y=y)

    if len(cell) == 0:
        cell = models.Cell(x=x, y=y, color=f"#{color}")
    else:
        cell = cell[0]
        cell.color = f"#{color}"

    cell.save()

    return JsonResponse(get_cells(), safe=False)
