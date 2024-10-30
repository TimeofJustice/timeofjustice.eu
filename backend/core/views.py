from PIL import Image
from django.conf import settings
from django.http import HttpRequest, JsonResponse, HttpResponse, HttpResponseRedirect
from inertia import render

from . import models
from .models import get_or_none


def error(request, status_code):
    return render(request, "Error", props={"status_code": status_code})


def index(request):
    return render(request, "Projects", props={
        "socials": [
            {
                "type": "github",
                "url": "https://github.com/TimeofJustice",
                "icon": "fa-brands fa-github"
            },
            {
                "type": "instagram",
                "url": "https://instagram.com/jonas.oel",
                "icon": "fa-brands fa-instagram"
            },
            {
                "type": "linkedin",
                "url": "https://linkedin.com/in/jonas-oelschner-2569441b3",
                "icon": "fa-brands fa-linkedin"
            },
            {
                "type": "twitter",
                "url": "https://twitter.com/timeofjustice_",
                "icon": "fa-brands fa-twitter"
            },
        ],
        "projects": [project.json() for project in models.Project.objects.all()]
    })


def project(request, id):
    return JsonResponse(models.Project.objects.get(id=id).json())


def project_details(request, id):
    project = get_or_none(models.Project, id=id)

    if not project:
        return error(request, 404)

    return render(request, "Project", props={"project": project.json()})


def project_images(request, name):
    response = HttpResponse(content_type="image/png")

    with open(f"{settings.FILE_DESTINATION}/images/project/{name}", "rb") as f:
        image = Image.open(f)
        image.save(response, "PNG")

    return response


def robot(request):
    lines = [
        "User-agent: *",
        "Disallow: /api/",
        "Disallow: /admin/",
        "Allow: /"
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
