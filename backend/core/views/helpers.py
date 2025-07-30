from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.http.response import FileResponse


# For serving static files in development, use the following views.
def static_files(path):
    if not Path(path).exists():
        return HttpResponse(status=404)

    return FileResponse(Path(path).open('rb'))

def favicon_images(request, name):
    path = f"{settings.FILE_DESTINATION}global/favicon/{name}"
    return static_files(path)

def project_images(request, name):
    path = f"{settings.FILE_DESTINATION}images/project/{name}"
    return static_files(path)


def project_video(request, name):
    path = f"{settings.FILE_DESTINATION}video/project/{name}"
    return static_files(path)


def project_images_lazy(request, name):
    path = f"{settings.FILE_DESTINATION}images/lazy/project/{name}"
    return static_files(path)


def tool_images(request, name):
    path = f"{settings.FILE_DESTINATION}images/tool/{name}"
    return static_files(path)


def profile_images(request, name):
    path = f"{settings.FILE_DESTINATION}images/profile/{name}"
    return static_files(path)


def games_cards(request, name):
    path = f"{settings.FILE_DESTINATION}images/games/cards/{name}"
    return static_files(path)


def robot(request):
    lines = [
        "User-agent: *",
        "Disallow: /api/",
        "Disallow: /admin/",
        "Disallow: /files/",
        "Allow: /",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
