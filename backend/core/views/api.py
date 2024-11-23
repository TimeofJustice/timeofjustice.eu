from django.http import JsonResponse

from .. import models


def project(request, id):
    return JsonResponse(models.Project.objects.get(id=id).json())