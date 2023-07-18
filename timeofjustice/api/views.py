import json
import os
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render


def get_json():
    with open(os.path.join(os.path.join(settings.BASE_DIR, 'api/data/projects.json'))) as file:
        projects = json.load(file)

    projects = sorted(projects, key=lambda d: d['status_id'])
    projects.reverse()

    return projects


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
