import datetime
import json
import os
import uuid

import numpy
import requests
from PIL import Image
from django.conf import settings

from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django_ratelimit.decorators import ratelimit

from .. import models
from ..helpers import rgb_to_hex, hex_to_rgb


@ratelimit(key='ip', rate='60/m')
def get_time_out(request):
    time_out = models.PlaceTimeOut.objects.all()[0].seconds
    return JsonResponse({"seconds": time_out}, safe=False)


def is_session_valid(session_id: str) -> bool:
    if session_id is None:
        return False

    sessions = models.Session.objects.filter(
        id=session_id,
        valid_until__gte=timezone.now()
    )

    if len(sessions) == 0:
        return False

    return True


def get_current_timeout():
    return models.PlaceTimeOut.objects.all()[0].seconds


def get_session(session_id: str) -> models.Session:
    return models.Session.objects.filter(
        id=session_id,
        valid_until__gte=timezone.now()
    )[0]


@ratelimit(key='ip', rate='60/m')
def get_last_placed(request):
    timeout_in_seconds = get_current_timeout()
    session_id = request.COOKIES.get("session")

    if not is_session_valid(session_id):
        return JsonResponse({"error": "No valid session"}, status=403)

    session = get_session(session_id)

    time = timezone.now()
    time_delta = datetime.timedelta(seconds=timeout_in_seconds)
    last_time_placed = session.last_placed

    if last_time_placed < time - time_delta:
        return JsonResponse({"seconds": 0}, safe=False)
    else:
        seconds = (last_time_placed - time + time_delta).total_seconds()
        return JsonResponse({"seconds": seconds}, safe=False)


class BodyContent:
    def __init__(self, request):
        body_unicode = request.body.decode('utf-8')

        self.body = json.loads(body_unicode)

    def get(self, key):
        return self.body.get(key)


@ratelimit(key='ip', rate='300/m')
@ensure_csrf_cookie
def place_set(request):
    timeout_in_seconds = get_current_timeout()
    session_id = request.COOKIES.get("session")

    if not is_session_valid(session_id):
        return JsonResponse({"error": "No valid session"}, status=403)

    session = get_session(session_id)
    time = timezone.now()

    if not session.last_placed < time - datetime.timedelta(seconds=timeout_in_seconds):
        seconds = (session.last_placed - time + datetime.timedelta(seconds=timeout_in_seconds)).total_seconds()

        return JsonResponse({"error": "You have cooldown", "seconds": seconds}, status=400)

    content = BodyContent(request)

    color = content.get("color")
    x = content.get("x")
    y = content.get("y")

    if color is None or x is None or y is None:
        return JsonResponse({"error": "Missing parameters"}, status=400)
    elif x < 0 or y < 0 or x > 1000 or y > 1000:
        return JsonResponse({"error": "Wrong coordinates"}, status=400)

    cells = models.Cell.objects.filter(x=x, y=y)

    if len(cells) == 0:
        cell = models.Cell(x=x, y=y, color=f"#{color}", placed_by=session_id)
    else:
        cell = cells[0]
        color_code = f"#{color}"

        if cell.color == color_code:
            return JsonResponse({"error": "Pixel has already that color"}, status=400)

        cell.color = color_code
        cell.placed_by = session_id

    session.last_placed = time

    cell.save()
    session.save()

    return JsonResponse({"x": cell.x, "y": cell.y, "color": cell.color}, safe=False)


@ratelimit(key='ip', rate='160/m')
def gen(request, from_x, from_y):
    if from_x < 0 or from_y < 0 or from_x > 1000 or from_y > 1000:
        return JsonResponse({"error": "Wrong coordinates"}, status=403)

    file_name = settings.FILE_DESTINATION + f"tiles/{from_x}_{from_y}.png"
    response = HttpResponse(content_type="image/png")

    if os.path.isfile(file_name):
        with open(file_name, "rb") as f:
            tile_image = Image.open(f)

            image = Image.new("RGB", tile_image.size, (255, 255, 255))
            image.paste(tile_image, (0, 0), tile_image)
    else:
        image = Image.new('RGB', (250, 250), (255, 255, 255))

    image.save(response, "PNG")

    return response


@ratelimit(key='ip', rate='1000/m')
def changes(request, from_x, from_y):
    if from_x < 0 or from_y < 0 or from_x > 1000 or from_y > 1000:
        return HttpResponse("Wrong coordinates")

    file_name = settings.FILE_DESTINATION + f"tiles/{from_x}_{from_y}.png"

    if os.path.isfile(file_name):
        with open(file_name, "rb") as f:
            tile_image = Image.new("RGBA", (250, 250))
            data = numpy.array(tile_image)

            date = datetime.datetime.utcfromtimestamp(int(request.GET.get("t")) / 1000)
            date = date - datetime.timedelta(seconds=1)
            date = timezone.make_aware(date)

            cells = models.Cell.objects.filter(
                x__gte=from_x,
                x__lte=from_x + 249,
                y__gte=from_y,
                y__lte=from_y + 249,
                last_modified__gte=date
            )

            if len(cells) != 0:
                for cell in cells:
                    data[cell.y - from_y][cell.x - from_x] = [int(cell.color[1:][i:i + 2], 16) for i in
                                                              (0, 2, 4)] + [255]

                tile_image = Image.fromarray(data)
    else:
        tile_image = Image.new('RGBA', (250, 250), (255, 255, 255, 0))

    response = HttpResponse(content_type="image/png")
    tile_image.save(response, "PNG")

    return response


@ratelimit(key='ip', rate='30/m')
def export(request, from_x, from_y, to_x, to_y, factor=1):
    if from_x < 0 or from_y < 0 or from_x > 1000 or from_y > 1000:
        return HttpResponse("Wrong coordinates")
    elif 10 < factor:
        return HttpResponse("Invalid scale-factor")

    size = (to_x - from_x + 1), (to_y - from_y + 1)

    image = Image.new('RGB', size, (255, 255, 255))
    image = image.resize(size, Image.NEAREST)
    data = numpy.array(image)

    cells = models.Cell.objects.filter(
        x__gte=from_x,
        x__lte=to_x,
        y__gte=from_y,
        y__lte=to_y
    )

    for cell in cells:
        data[cell.y - from_y][cell.x - from_x] = [int(cell.color[1:][i:i + 2], 16) for i in (0, 2, 4)]

    image = Image.fromarray(data)

    scaled_size = size[0] * factor, size[1] * factor

    image = image.resize(scaled_size, Image.NEAREST)

    response = HttpResponse(content_type="image/png")
    image.save(response, "png", quality=100)

    return response


@ratelimit(key='ip', rate='60/m')
def validate_captcha(request):
    if request.method == "POST":
        response_json = {}

        content = BodyContent(request)

        captcha_rs = content.get('token')
        url = "https://www.google.com/recaptcha/api/siteverify"

        params = {
            'secret': settings.CONFIG_PARSER["DEFAULT"]["SECRET_KEY"],
            'response': captcha_rs,
            'remoteip': request.META['REMOTE_ADDR']
        }

        verify_rs = requests.get(url, params=params, verify=True)
        verify_rs = verify_rs.json()

        response_json["status"] = verify_rs.get("success", False)
        response_json['message'] = verify_rs.get('error-codes', None) or "Unspecified error."

        response = JsonResponse(response_json, safe=False)

        if response_json["status"]:
            if not is_session_valid(request.COOKIES.get("session")):
                create_session(response)
        else:
            response.set_cookie("session", "None", expires=timezone.now())

        return response


def create_session(response):
    session = uuid.uuid4()
    response.set_cookie("session", session, expires=timezone.now() + datetime.timedelta(hours=6))
    session = models.Session(id=session, last_placed=timezone.now(),
                              valid_until=timezone.now() + datetime.timedelta(hours=6))
    session.save()


@ratelimit(key='ip', rate='50/m')
def get_overlay(request, overlay_name):
    json_images = []

    overlays = models.Overlay.objects.filter(name=overlay_name)

    if len(overlays) == 0:
        return JsonResponse([], safe=False)
    else:
        overlay = overlays[0]

    images = models.OverlayImage.objects.filter(overlay=overlay)

    for image_entry in images:
        image_name = os.path.basename(image_entry.layout.path)
        image_path = settings.FILE_DESTINATION + f"layouts/pixels/{image_name}"

        image = Image.open(image_path)

        arr = numpy.array(image)
        reshaped = arr.reshape(-1, arr.shape[-1])

        colors = numpy.unique(reshaped[(reshaped[:, 3] == 255)], axis=0)
        colors = [rgb_to_hex(color) for color in colors]

        json_images.append({
            "url": f"/images/layouts/pixels/{image_name}?t={timezone.now().timestamp()}",
            "x": image_entry.x,
            "y": image_entry.y,
            "width": image_entry.width,
            "height": image_entry.height,
            "colors": colors
        })

    return JsonResponse(json_images, safe=False)


@ratelimit(key='ip', rate='15/m')
def get_overlay_color(request, overlay_name, index, color):
    json_images = []

    overlays = models.Overlay.objects.filter(name=overlay_name)

    if len(overlays) == 0:
        return JsonResponse({"error": "No valid overlay"}, safe=False)
    else:
        overlay = overlays[0]

    images = models.OverlayImage.objects.filter(overlay=overlay)

    if len(images) < index:
        return JsonResponse({"error": "No valid index"}, safe=False)

    with open(images[index].layout.path, "rb") as f:
        overlay_image = Image.open(f)

        rgb_color = hex_to_rgb(f"#{color}")

        filtered_image = Image.new("RGBA", overlay_image.size)

        for x in range(overlay_image.width):
            for y in range(overlay_image.height):
                r, g, b, a = overlay_image.getpixel((x, y))

                if (r, g, b) == rgb_color and a == 255:
                    # Setze die Farbwerte des Pixels im neuen Bild
                    filtered_image.putpixel((x, y), (r, g, b, a))
                else:
                    # Setze den Alpha-Kanal des Pixels auf 0, um ihn transparent zu machen
                    filtered_image.putpixel((x, y), (r, g, b, 0))

        response = HttpResponse(content_type="image/png")

        filtered_image.save(response, "PNG")

        return response


@ratelimit(key='ip', rate='90/m')
def discover(request):
    last_update = int(request.GET.get("t")) / 1000

    tiles = models.Tile.objects.all()

    tiles_with_update = []

    for tile in tiles:
        tile_update = tile.last_updated.replace(tzinfo=timezone.now()).timestamp()

        if tile_update > last_update:
            tiles_with_update.append(
                {
                    "x": tile.x,
                    "y": tile.y,
                    "src": f"/images/{tile.x}_{tile.y}.png"
                }
            )

    return JsonResponse(tiles_with_update, safe=False)


@ratelimit(key='ip', rate='600/m')
def get_color(request, x, y):
    cells = models.Cell.objects.filter(x=x, y=y)

    if len(cells) != 0:
        cell = cells[0]

        return JsonResponse({"color": cell.color}, safe=False)
    else:
        return JsonResponse({"color": "#FFFFFF"}, safe=False)
