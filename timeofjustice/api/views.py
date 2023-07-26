import datetime
import json
import os
from PIL.Image import Resampling
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from . import models
import requests
import configparser


def get_json():
    json_projects = []
    projects = models.Project.objects.all()

    for project in projects:
        serialized_obj = model_to_dict(project)

        serialized_obj["status_id"] = project.status.id
        serialized_obj["status"] = project.status.name

        serialized_obj["languages"] = []

        for language in project.languages.all():
            serialized_obj["languages"].append(language.name)

        serialized_obj["images"] = []

        for image in project.image_set.all():
            image_elements = image.image.url.split("/")[6::]
            preview_elements = image.preview.url.split("/")[6::]
            serialized_obj["images"].append([["/".join(image_elements), "/".join(preview_elements)], image.alt])

        json_projects.append(serialized_obj)

    json_projects = sorted(json_projects, key=lambda k: k["status_id"])
    json_projects.reverse()

    return json_projects


def set_session_cookie(request):
    import uuid

    if request.COOKIES.get("session") is None:
        return uuid.uuid4()
    else:
        return request.COOKIES.get("session")


@ensure_csrf_cookie
def project(request, project_id):
    projects = get_json()

    if len(projects) < project_id:
        return JsonResponse({"error": "ProjectData not found."}, status=404)

    return JsonResponse(projects[project_id], safe=False)


@ensure_csrf_cookie
def projects_list(request):
    projects = get_json()

    return JsonResponse(projects, safe=False)


@ensure_csrf_cookie
def index(request):
    session = set_session_cookie(request)

    context = {
        "mode": "dark"
    }

    if request.COOKIES.get("mode") is not None:
        context["mode"] = request.COOKIES.get("mode")

    response = render(request, "index.html", context)
    response.set_cookie("session", session)
    return response


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


def get_time_out(request):
    time_out = models.PlaceTimeOut.objects.all()[0].seconds
    return JsonResponse({"seconds": time_out}, safe=False)


def get_last_placed(request):
    session_id = request.COOKIES.get("session")

    if session_id is None:
        return JsonResponse({"seconds": 0}, safe=False)

    # check if session id exists
    session = models.LastPlaced.objects.filter(id=session_id)

    if len(session) == 0:
        return JsonResponse({"seconds": 0}, safe=False)

    timeout_in_seconds = models.PlaceTimeOut.objects.all()[0].seconds

    time = datetime.datetime.now(tz=datetime.timezone.utc)

    if session[0].timestamp < time - datetime.timedelta(seconds=timeout_in_seconds):
        return JsonResponse({"seconds": 0}, safe=False)
    else:
        seconds = (session[0].timestamp - time + datetime.timedelta(seconds=timeout_in_seconds)).total_seconds()
        return JsonResponse({"seconds": seconds}, safe=False)


@ensure_csrf_cookie
def place_set(request):
    session_id = request.COOKIES.get("session")

    if session_id is None:
        return JsonResponse({"error": "Missing session id"}, status=400)

    sessions = models.LastPlaced.objects.filter(id=session_id)
    timeout_in_seconds = models.PlaceTimeOut.objects.all()[0].seconds

    if len(sessions) != 0:
        time = datetime.datetime.now(tz=datetime.timezone.utc)

        if not sessions[0].timestamp < time - datetime.timedelta(seconds=timeout_in_seconds):
            seconds = (sessions[0].timestamp - time + datetime.timedelta(seconds=timeout_in_seconds)).total_seconds()

            return JsonResponse({"error": "You have cooldown", "seconds": seconds}, status=400)

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body

    color = content.get("color")
    x = content.get("x")
    y = content.get("y")

    if color is None or x is None or y is None:
        return JsonResponse({"error": "Missing parameters"}, status=400)
    elif x < 0 or y < 0 or x > 1000 or y > 1000:
        return JsonResponse({"error": "Wrong coordinates"}, status=400)

    cell = models.Cell.objects.filter(x=x, y=y)

    if len(cell) == 0:
        cell = models.Cell(x=x, y=y, color=f"#{color}", placed_by=session_id)
    else:
        cell = cell[0]
        cell.color = f"#{color}"
        cell.placed_by = session_id

    cell.save()

    if len(sessions) == 0:
        session = models.LastPlaced(id=session_id, timestamp=content.get("timestamp"))
    else:
        session = sessions[0]
        session.timestamp = datetime.datetime.now()

    session.save()

    return JsonResponse({"x": cell.x, "y": cell.y, "color": cell.color}, safe=False)


def gen(request, from_x, from_y):
    destination = 'home/jonas/timeofjustice.eu/timeofjustice/data/images/'

    if os.name == 'nt':
        destination = 'C:/xampp/htdocs/timeofjustice.eu/timeofjustice/static/data/images/'

    from PIL import Image

    if from_x < 0 or from_y < 0 or from_x > 1000 or from_y > 1000:
        return HttpResponse("Wrong coordinates")

    file_name = destination + f"{from_x}_{from_y}.png"

    if os.path.isfile(file_name):
        image = Image.open(file_name)
        image = image.convert("RGBA")
        image = image.resize((250, 250), Image.ANTIALIAS)
    else:
        # Create a new image of the size required with transparent background
        image = Image.new('RGBA', (250, 250), (255, 255, 255, 0))

    response = HttpResponse(content_type="image/png")
    image.save(response, "PNG")

    return response


def export(request, from_x, from_y, to_x, to_y, factor=1):
    destination = 'home/jonas/timeofjustice.eu/timeofjustice/data/images/'

    if os.name == 'nt':
        destination = 'C:/xampp/htdocs/timeofjustice.eu/timeofjustice/static/data/images/'

    from PIL import Image
    import numpy

    if from_x < 0 or from_y < 0 or from_x > 1000 or from_y > 1000:
        return HttpResponse("Wrong coordinates")

    size = (to_x - from_x + 1), (to_y - from_y + 1)

    image = Image.new('RGB', size, (255, 255, 255))
    image = image.resize(size, Image.ANTIALIAS)
    data = numpy.array(image)

    cells = models.Cell.objects.filter(
        x__gte=from_x,
        x__lte=to_x,
        y__gte=from_y,
        y__lte=to_y
    )

    print(cells)

    for cell in cells:
        data[cell.y - from_y][cell.x - from_x] = [int(cell.color[1:][i:i + 2], 16) for i in (0, 2, 4)]

    image = Image.fromarray(data)

    scaled_size = size[0] * factor, size[1] * factor

    image = image.resize(scaled_size, Resampling.NEAREST)

    response = HttpResponse(content_type="image/png")
    image.save(response, "PNG")

    return response


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_captcha(request):
    if request.method == "POST":
        config_path = '/home/jonas/timeofjustice.eu/timeofjustice/data/config.ini'

        if os.name == 'nt':
            config_path = 'C:/Users/ogtim/Documents/GitHub/timeofjustice.eu/timeofjustice/data/config.ini'

        config = configparser.ConfigParser()
        config.read(config_path)

        response = {}
        data = request.POST
        captcha_rs = data.get('token')
        url = "https://www.google.com/recaptcha/api/siteverify"
        params = {
            'secret': config["DEFAULT"]["SECRET_KEY"],
            'response': captcha_rs,
            'remoteip': get_client_ip(request)
        }
        verify_rs = requests.get(url, params=params, verify=True)
        verify_rs = verify_rs.json()
        response["status"] = verify_rs.get("success", False)
        response['message'] = verify_rs.get('error-codes', None) or "Unspecified error."

        return JsonResponse(response, safe=False)
