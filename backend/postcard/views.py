from django.http.response import JsonResponse
from inertia import render

from core.helpers import default_props


def index(request, postcard_id = None, **kwargs):
    page_props = {
        "id": postcard_id if postcard_id else "default_postcard_id",
        "message": "Hallo, dies ist eine Postkarte",
        "greetings": "Mit viel Liebe, dein Freund",
    }

    return render(request, "PostcardPage", props=default_props(page_props, request, **kwargs))


def send_postcard(request, **kwargs):
    page_props = {
        "id": "dfsdfghfh",
    }

    return JsonResponse({
        "status": "success",
        "data": page_props,
    })


def report_postcard(request, postcard_id, **kwargs):
    page_props = {
        "id": postcard_id,
    }

    return JsonResponse({
        "status": "success",
        "data": page_props,
    })
