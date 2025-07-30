from django.http import JsonResponse

from core import models
from core.models import get_or_none


def project(request, project_id):
    project = get_or_none(models.Project, id=project_id)

    if not project:
        return JsonResponse({"error": "Project not found"}, status=404)

    return JsonResponse(project)
