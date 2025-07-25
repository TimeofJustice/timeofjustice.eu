from django.conf import settings
from django.http import HttpResponse
from django.http.response import FileResponse

# For serving static files in development, use the following views.
def favicon_images(request, name):
    return FileResponse(open(f"{settings.FILE_DESTINATION}global/favicon/{name}", 'rb'))

def project_images(request, name):
    return FileResponse(open(f"{settings.FILE_DESTINATION}images/project/{name}", 'rb'))


def project_video(request, name):
    return FileResponse(open(f"{settings.FILE_DESTINATION}video/project/{name}", 'rb'))


def project_images_lazy(request, name):
    return FileResponse(open(f"{settings.FILE_DESTINATION}images/lazy/project/{name}", 'rb'))


def tool_images(request, name):
    return FileResponse(open(f"{settings.FILE_DESTINATION}images/tool/{name}", 'rb'))


def profile_images(request, name):
    return FileResponse(open(f"{settings.FILE_DESTINATION}images/profile/{name}", 'rb'))


def games_cards(request, name):
    return FileResponse(open(f"{settings.FILE_DESTINATION}images/games/cards/{name}", 'rb'))


def robot(request):
    lines = [
        "User-agent: *",
        "Disallow: /api/",
        "Disallow: /admin/",
        "Allow: /"
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")