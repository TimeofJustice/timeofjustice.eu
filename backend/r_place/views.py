import django.shortcuts
from inertia import render

from core.helpers import props


def chat(request):
    return django.shortcuts.render(request, "chat/index.html")


def room(request, room_name):
    return django.shortcuts.render(request, "chat/room.html", {"room_name": room_name})


def index(request):
    page_props = {

    }

    return render(request, "RPlace", props=props(page_props))
