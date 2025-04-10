from django.conf import settings
from inertia import render

from .. import models
from ..helpers import props
from ..models import get_or_none, Profile


def error(request, status_code):
    page_props = {
        "status_code": status_code
    }

    return render(request, "Error", props=props(page_props))


def index(request):
    profile = get_or_none(Profile, id=1)

    page_props = {
        "profile": profile.json() if profile else None,
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
        ],
        "projects": [project.json() for project in models.Project.objects.all()],
        "tools": [tool.json() for tool in models.Tool.objects.all()],
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