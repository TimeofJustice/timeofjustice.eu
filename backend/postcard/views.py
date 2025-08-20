from django.http.response import JsonResponse
from inertia import render

from core.helpers import default_props


def index(request, postcard_id = None, **kwargs):
    page_props = {
        "postcard": {
            "id": postcard_id if postcard_id else "default_postcard_id",
            "message": "Hallo, dies ist eine Postkarte",
            "greetings": "Mit viel Liebe, dein Freund",
            "design": {
                "id": 0,
                "pageColor": "#ffbaba",
                "backgroundColor": "#fff",
                "stampColor": "#e5b473",
                "accentColor": "#e57373",
                "textColor": "#333333",
                "icon": "twemoji:teddy-bear",
            },
        },
        "designs": [
            {
                "id": 0,
                "pageColor": "#ffbaba",
                "backgroundColor": "#fff",
                "stampColor": "#e5b473",
                "accentColor": "#e57373",
                "textColor": "#333333",
                "icon": "twemoji:teddy-bear",
            },
            {
                "id": 2,
                "pageColor": "#ffdfba",
                "backgroundColor": "#fff",
                "stampColor": "#e5b473",
                "accentColor": "#e57373",
                "textColor": "#333333",
                "icon": "twemoji:cat",
            },
            {
                "id": 3,
                "pageColor": "#1a1a1a",
                "backgroundColor": "#000000",
                "stampColor": "#ffd700",
                "accentColor": "#bfa14a",
                "textColor": "#ffd700",
                "icon": "twemoji:star",
            },
        ],
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
