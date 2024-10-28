from django.http import HttpRequest, JsonResponse
from inertia import render


def index(request):
    return render(request, "Projects", props={
        "socials": [
            {
                "type": "github",
                "url": "https://github.com/TimeofJustice",
                "icon": "fa-brands fa-github"
            },
            {
                "type": "instagram",
                "url": "https://instagram.com/jonas.oel",
                "icon": "fa-brands fa-instagram"
            },
            {
                "type": "linkedin",
                "url": "https://linkedin.com/in/jonas-oelschner-2569441b3",
                "icon": "fa-brands fa-linkedin"
            },
            {
                "type": "twitter",
                "url": "https://twitter.com/timeofjustice_",
                "icon": "fa-brands fa-twitter"
            },
        ]
    })

def project(request, id):
    return JsonResponse({
        "id": id,
        "title": "Project Name",
        "description": "Project Description",
    })