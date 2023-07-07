from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

projects = [
    {
        "name": "TimeofJustice",
        "status": "In Development",
        "languages": ["Python", "Django"],
        "git": "https://github.com/TimeofJustice/Angewandte-Informatik",
        "images": [
            "https://www.thoughtco.com/thmb/KH0SxyxmymjQtoTffjClEQiGOB0=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-116248249-5be59c3cc9e77c00514fed87.jpg",
            "https://www.shutterstock.com/image-vector/links-colorful-vector-typography-web-260nw-1617964219.jpg",
            "https://kinsta.com/de/wp-content/uploads/sites/5/2019/11/ankerlinks-wordpress.png"
        ],
        "description": "This is a description of the project. It is a very cool project."*10
    },
    {
        "name": "TimeofJustice",
        "status": "In Development",
        "languages": ["Python", "Django"],
        "images": [
            "https://image.geo.de/30103062/t/c7/v3/w1440/r1.7778/-/rechts-links-teaser-jpg--57167-.jpg"
        ],
        "description": "This is a description of the project. It is a very cool project too."*5
    }
]*10


def index(request):
    context = {
        "title": "Projects - TimeofJustice",
        "projects": projects,
        "mode": "dark"
    }

    if request.COOKIES.get("mode") is not None:
        context["mode"] = request.COOKIES.get("mode")

    response = render(request, "index.html", context)

    return response


def project(request, project_id):
    return JsonResponse(projects[project_id], safe=False)


def robot(request):
    lines = [
        "User-Agent: *",
        "Disallow: /"
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
