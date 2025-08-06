from inertia import render

from core import models
from core.helpers import default_props, get_or_none


def error(request, status_code):
    page_props = {
        "statusCode": status_code,
    }

    return render(request, "ErrorPage", props=default_props(page_props))


def index(request):
    profile = get_or_none(models.Profile, id=1)

    page_props = {
        "profile": profile.json() if profile else None,
        "socials": [
            {
                "type": "github",
                "url": "https://github.com/TimeofJustice",
                "icon": "fa-brands fa-github",
            },
            {
                "type": "instagram",
                "url": "https://instagram.com/jonas.oel",
                "icon": "fa-brands fa-instagram",
            },
            {
                "type": "linkedin",
                "url": "https://linkedin.com/in/jonas-oelschner-2569441b3",
                "icon": "fa-brands fa-linkedin",
            },
        ],
        "projects": [project.json() for project in models.Project.objects.all()],
        "tools": [tool.json() for tool in models.Tool.objects.all()],
    }

    return render(request, "ProjectsPage", props=default_props(page_props))


def project_details(request, project_id):
    project = get_or_none(models.Project, id=project_id)

    if not project:
        return error(request, 404)

    page_props = {
        "project": project.json(),
    }

    return render(request, "ProjectPage", props=default_props(page_props))
