from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django_ratelimit.exceptions import Ratelimited


@ensure_csrf_cookie
def index(request):
    context = {
        "mode": "dark"
    }

    if request.COOKIES.get("mode") is not None:
        context["mode"] = request.COOKIES.get("mode")

    response = render(request, "index.html", context)
    return response


def ratelimited_error(request, exception: Ratelimited):
    return JsonResponse({'error': 'Too many requests'}, status=429)


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
