from django.conf import settings
from inertia import render

from .. import models
from ..models import get_or_none


def props(props):
    return {
        "production": settings.DEBUG is False,
        **props
    }


def error(request, status_code):
    page_props = {
        "status_code": status_code
    }

    return render(request, "Error", props=props(page_props))


def index(request):
    page_props = {
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
    }

    return render(request, "Projects", props=props(page_props))


def project_details(request, id):
    project = get_or_none(models.Project, id=id)

    if not project:
        return error(request, 404)

    page_props = {
        "project": project.json()
    }

    return render(request, "Project", props=props(page_props))