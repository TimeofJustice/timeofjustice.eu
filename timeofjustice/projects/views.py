from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    context = {
        "title": "Projects - TimeofJustice",
        "projects": [
            {
                "name": "TimeofJustice",
                "status": "In Development",
                "languages": ["Python", "Django"],
                "git": "https://github.com/TimeofJustice/Angewandte-Informatik"
            },
            {
                "name": "TimeofJustice",
                "status": "In Development",
                "languages": ["Python", "Django"]
            }
        ],
        "mode": "dark"
    }

    if request.COOKIES.get("mode") is not None:
        context["mode"] = request.COOKIES.get("mode")

    response = render(request, "index.html", context)

    return response


def robot(request):
    lines = [
        "User-Agent: *",
        "Disallow: /"
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
