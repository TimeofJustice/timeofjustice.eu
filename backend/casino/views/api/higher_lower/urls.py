from django.urls import path

from .api import start, higher, lower, draw, leave

urlpatterns = [
    path("start/", start, name="start"),

    path("higher/", higher, name="higher"),
    path("draw/", draw, name="draw"),
    path("lower/", lower, name="lower"),

    path("leave/", leave, name="leave"),
]
