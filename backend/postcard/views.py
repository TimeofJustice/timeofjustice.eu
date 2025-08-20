import uuid

from django.http.response import JsonResponse
from inertia import render

from core.helpers import BodyContent, default_props
from core.views.pages import error
from postcard import models


def index(request, postcard_id = None, **kwargs):
    if postcard_id is None:
        postcard = models.Postcard.objects.filter(showcased=True, amount_reports__lt=5).order_by("?").first()
    else:
        postcard = models.Postcard.objects.filter(id=postcard_id, amount_reports__lt=5).first()

        if postcard is None:
            return error(request, 404)

    page_props = {
        "postcard": postcard.json() if postcard else None,
        "designs": [design.json() for design in models.Design.objects.all()],
        "navbarSize": "small",
    }

    return render(request, "PostcardPage", props=default_props(page_props, request, **kwargs))


def send_postcard(request, **kwargs):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "method_not_allowed",
        }, status=405)

    post_data = BodyContent(request)

    if not post_data.get("message") or not post_data.get("greetings") or not post_data.get("designId"):
        return JsonResponse({
            "status": "error",
            "message": "missing_fields",
        }, status=400)

    design = models.Design.objects.filter(id=post_data.get("designId")).first()

    if design is None:
        return JsonResponse({
            "status": "error",
            "message": "design_not_found",
        }, status=404)

    if len(post_data.get("message")) > 500 or len(post_data.get("greetings")) > 50:
        return JsonResponse({
            "status": "error",
            "message": "message_too_long" if len(post_data.get("message")) > 500 else "greetings_too_long",
        }, status=400)

    if len(post_data.get("message")) < 1 or len(post_data.get("greetings")) < 1:
        return JsonResponse({
            "status": "error",
            "message": "message_too_short" if len(post_data.get("message")) < 5 else "greetings_too_short",
        }, status=400)

    postcard_id = str(uuid.uuid4())[:6]
    while models.Postcard.objects.filter(id=postcard_id).exists():
        postcard_id = str(uuid.uuid4())[:6]

    postcard = models.Postcard(
        id=postcard_id,
        message=post_data.get("message"),
        greetings=post_data.get("greetings"),
        design=design,
    )
    postcard.save()

    return JsonResponse({
        "status": "success",
        "message": "postcard_sent",
        "data": postcard.json(),
    })


def report_postcard(request, postcard_id, **kwargs):
    postcard = models.Postcard.objects.filter(id=postcard_id).first()

    if postcard is None:
        return JsonResponse({
            "status": "error",
            "message": "not_found",
        }, status=404)

    postcard.amount_reports += 1
    postcard.save()

    return JsonResponse({
        "status": "success",
        "message": "reported_successfully",
    })
