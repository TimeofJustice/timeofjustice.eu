from django.urls import path

from .api import start

urlpatterns = [
    path("start/", start, name="start"),
]
