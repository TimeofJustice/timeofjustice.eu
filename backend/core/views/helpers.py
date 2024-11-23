from PIL import Image
from django.conf import settings
from django.http import HttpResponse


def project_images(request, name):
    response = HttpResponse(content_type="image/png")

    with open(f"{settings.FILE_DESTINATION}/images/project/{name}", "rb") as f:
        image = Image.open(f)
        image.save(response, "PNG")

    return response


def project_images_lazy(request, name):
    response = HttpResponse(content_type="image/png")

    with open(f"{settings.FILE_DESTINATION}/images/lazy/project/{name}", "rb") as f:
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