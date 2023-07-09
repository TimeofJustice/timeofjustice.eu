import json
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

projects = json.load(open(os.getcwd() + "/timeofjustice/projects/data/projects.json", "r"))


def index(request):
    newlist = sorted(projects, key=lambda d: d['status_id'])
    newlist.reverse()

    context = {
        "title": "Projects - TimeofJustice",
        "projects": newlist,
        "mode": "dark"
    }

    if request.COOKIES.get("mode") is not None:
        context["mode"] = request.COOKIES.get("mode")

    response = render(request, "index.html", context)
    return response


def project(request, project_id):
    return JsonResponse(projects[project_id], safe=False)


def robot(request):
    lines = [
        "User-Agent: *",
        "Disallow: /"
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
