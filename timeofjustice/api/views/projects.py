from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from . import set_session_cookie
from .. import models


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


@ensure_csrf_cookie
def get_project(request, project_id):
    projects = get_json()

    if len(projects) < project_id:
        return JsonResponse({"error": "ProjectData not found."}, status=404)

    return JsonResponse(projects[project_id], safe=False)


@ensure_csrf_cookie
def projects_list(request):
    projects = get_json()

    return JsonResponse(projects, safe=False)


@ensure_csrf_cookie
def index(request):
    session = set_session_cookie(request)

    context = {
        "mode": "dark"
    }

    if request.COOKIES.get("mode") is not None:
        context["mode"] = request.COOKIES.get("mode")

    response = render(request, "index.html", context)
    response.set_cookie("session", session)
    return response
