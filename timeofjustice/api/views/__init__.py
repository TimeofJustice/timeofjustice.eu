from django.http import HttpResponseRedirect, HttpResponse


def set_session_cookie(request):
    import uuid

    if request.COOKIES.get("session") is None:
        return uuid.uuid4()
    else:
        return request.COOKIES.get("session")


def handler404(request, *args, **kwargs):
    return HttpResponseRedirect('/')


def robot(request):
    lines = [
        "User-agent: *",
        "Disallow: /api/",
        "Disallow: /admin/",
        "Allow: /"
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
