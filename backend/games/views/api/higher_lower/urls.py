from django.urls import path

from .api import draw, higher, leave, lower, start

urlpatterns = [
    path("start/", start, name="start"),

    path("higher/", higher, name="higher"),
    path("draw/", draw, name="draw"),
    path("lower/", lower, name="lower"),

    path("leave/", leave, name="leave"),
]
