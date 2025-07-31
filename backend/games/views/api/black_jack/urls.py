from django.urls import path

from .api import hit, stand, start

urlpatterns = [
    path("start/", start, name="start"),

    path("hit/", hit, name="hit"),
    path("stand/", stand, name="stand"),
]
