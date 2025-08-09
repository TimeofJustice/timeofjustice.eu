
from inertia import render

from core import models
from core.helpers import call_view_by_url, default_props, get_or_none


def error(request, status_code, offcanvas_component=None, **kwargs):
    page_props = {
        "statusCode": status_code,
    }

    return render(request, "ErrorPage", props=default_props(page_props, request, offcanvas_component=offcanvas_component, **kwargs))


def index(request, offcanvas_component=None, **kwargs):
    profile = get_or_none(models.Profile, id=1)

    page_props = {
        "profile": profile.json() if profile else None,
        "socials": [
            {
                "type": "github",
                "url": "https://github.com/TimeofJustice",
                "icon": "line-md:github",
            },
            {
                "type": "instagram",
                "url": "https://instagram.com/jonas.oel",
                "icon": "line-md:instagram",
            },
            {
                "type": "linkedin",
                "url": "https://linkedin.com/in/jonas-oelschner-2569441b3",
                "icon": "line-md:linkedin",
            },
        ],
        "projects": [project.json() for project in models.Project.objects.all()],
        "tools": [tool.json() for tool in models.Tool.objects.all()],
    }

    return render(request, "ProjectsPage", props=default_props(page_props, request, offcanvas_component=offcanvas_component, **kwargs))


def project_details(request, project_id):
    project = get_or_none(models.Project, id=project_id)

    if not project:
        return error(request, 404)

    page_props = {
        "project": project.json(),
    }

    offcanvas_source = request.headers.get("X-Offcanvas-Source")
    if offcanvas_source:
        return call_view_by_url(
            offcanvas_source, request=request, error_callback=error, offcanvas_component="ProjectPage", **page_props,
        )

    return render(request, "ProjectPage", props=default_props(page_props, request))

