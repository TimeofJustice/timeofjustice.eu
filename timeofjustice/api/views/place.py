import configparser
import datetime
import json
import os
import re

import numpy
import requests
from PIL import Image
from django.conf import settings

from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django_ratelimit.decorators import ratelimit

from .. import models


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def rgb_to_hex(rgb):
    return '#{0:02x}{1:02x}{2:02x}'.format(rgb[0], rgb[1], rgb[2])


@ratelimit(key='ip', rate='60/m')
def get_time_out(request):
    time_out = models.PlaceTimeOut.objects.all()[0].seconds
    return JsonResponse({"seconds": time_out}, safe=False)


@ratelimit(key='ip', rate='60/m')
def get_last_placed(request):
    timeout_in_seconds = models.PlaceTimeOut.objects.all()[0].seconds
    session_id = request.COOKIES.get("session")

    if session_id is None:
        session = models.LastPlaced(id=session_id, timestamp=timezone.now())
        session.save()
        return JsonResponse({"seconds": timeout_in_seconds}, safe=False)

    sessions = models.LastPlaced.objects.filter(id=session_id)

    if len(sessions) == 0:
        session = models.LastPlaced(id=session_id, timestamp=timezone.now())
        session.save()
        return JsonResponse({"seconds": timeout_in_seconds}, safe=False)

    time = timezone.now()

    if sessions[0].timestamp < time - datetime.timedelta(seconds=timeout_in_seconds):
        return JsonResponse({"seconds": 0}, safe=False)
    else:
        seconds = (sessions[0].timestamp - time + datetime.timedelta(seconds=timeout_in_seconds)).total_seconds()
        return JsonResponse({"seconds": seconds}, safe=False)


@ratelimit(key='ip', rate='300/m')
@ensure_csrf_cookie
def place_set(request):
    session_id = request.COOKIES.get("session")

    if session_id is None:
        return JsonResponse({"error": "Missing session id"}, status=400)

    sessions = models.LastPlaced.objects.filter(id=session_id)
    timeout_in_seconds = models.PlaceTimeOut.objects.all()[0].seconds

    if len(sessions) != 0:
        time = timezone.now()

        if not sessions[0].timestamp < time - datetime.timedelta(seconds=timeout_in_seconds):
            seconds = (sessions[0].timestamp - time + datetime.timedelta(seconds=timeout_in_seconds)).total_seconds()

            return JsonResponse({"error": "You have cooldown", "seconds": seconds}, status=400)
    else:
        return JsonResponse({"error": "You have cooldown", "seconds": timeout_in_seconds}, status=400)

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
        session = models.LastPlaced(id=session_id, timestamp=timezone.now())
    else:
        session = sessions[0]
        session.timestamp = timezone.now()

    session.save()

    return JsonResponse({"x": cell.x, "y": cell.y, "color": cell.color}, safe=False)


@ratelimit(key='ip', rate='160/m')
def gen(request, from_x, from_y):
    if from_x < 0 or from_y < 0 or from_x > 1000 or from_y > 1000:
        return HttpResponse("Wrong coordinates")

    file_name = settings.FILE_DESTINATION + f"{from_x}_{from_y}.png"

    if os.path.isfile(file_name):
        try:
            with open(file_name, "rb") as f:
                image = Image.open(f)

                white_background = Image.new("RGB", image.size, (255, 255, 255))
                white_background.paste(image, (0, 0), image)

                response = HttpResponse(content_type="image/png")
                white_background.save(response, "PNG")

                return response
        except IOError:
            print("Error reading")
    else:
        image = Image.new('RGBA', (250, 250), (255, 255, 255, 255))

    response = HttpResponse(content_type="image/png")
    image.save(response, "PNG")

    return response


def changes(request, from_x, from_y):
    if from_x < 0 or from_y < 0 or from_x > 1000 or from_y > 1000:
        return HttpResponse("Wrong coordinates")

    file_name = settings.FILE_DESTINATION + f"{from_x}_{from_y}.png"

    if os.path.isfile(file_name):
        try:
            with open(file_name, "rb") as f:
                image = Image.new("RGBA", (250, 250))
                data = numpy.array(image)

                date = datetime.datetime.fromtimestamp(int(request.GET.get("t")) / 1000)
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

                    image = Image.fromarray(data)

                response = HttpResponse(content_type="image/png")
                image.save(response, "PNG")

                return response
        except IOError:
            print("Error reading")
    else:
        image = Image.new('RGBA', (250, 250), (255, 255, 255, 0))

    response = HttpResponse(content_type="image/png")
    image.save(response, "PNG")

    return response


@ratelimit(key='ip', rate='30/m')
def export(request, from_x, from_y, to_x, to_y, factor=1):
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

    for cell in cells:
        data[cell.y - from_y][cell.x - from_x] = [int(cell.color[1:][i:i + 2], 16) for i in (0, 2, 4)]

    image = Image.fromarray(data)

    scaled_size = size[0] * factor, size[1] * factor

    image = image.resize(scaled_size, Image.NEAREST)

    response = HttpResponse(content_type="image/png")
    image.save(response, "PNG")

    return response


@ratelimit(key='ip', rate='60/m')
def validate_captcha(request):
    if request.method == "POST":
        response = {}
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        data = body
        captcha_rs = data.get('token')
        url = "https://www.google.com/recaptcha/api/siteverify"

        params = {
            'secret': settings.CONFIG_PARSER["DEFAULT"]["SECRET_KEY"],
            'response': captcha_rs,
            'remoteip': get_client_ip(request)
        }
        verify_rs = requests.get(url, params=params, verify=True)
        verify_rs = verify_rs.json()
        response["status"] = verify_rs.get("success", False)
        response['message'] = verify_rs.get('error-codes', None) or "Unspecified error."

        return JsonResponse(response, safe=False)


@ratelimit(key='ip', rate='50/m')
def get_overlay(request, overlay_name):
    json_images = []
    overlays = models.Overlay.objects.filter(name=overlay_name)

    if len(overlays) == 0:
        return JsonResponse([], safe=False)
    else:
        overlay = overlays[0]

    images = models.OverlayImage.objects.filter(overlay=overlay)

    for image in images:
        image_name = os.path.basename(image.image.path)

        img = Image.open(image.image.path)
        arr = numpy.array(img)
        reshaped = arr.reshape(-1, arr.shape[-1])
        colors = numpy.unique(reshaped, axis=0)

        colors = [rgb_to_hex(color) for color in colors]

        json_images.append({
            "url": f"/images/{image_name}",
            "x": image.x,
            "y": image.y,
            "width": image.width,
            "height": image.height,
            "colors": colors
        })

    return JsonResponse(json_images, safe=False)


def discover(request):
    last_update = int(request.GET.get("t")) / 1000

    tiles = models.Tiles.objects.all()

    tiles_with_update = []

    for tile in tiles:
        tile_update = tile.last_updated.replace(tzinfo=timezone.utc).timestamp()

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
