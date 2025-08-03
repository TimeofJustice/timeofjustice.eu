from django.urls import path

from games.views.sic_bo.api import start

urlpatterns = [
    path("start/", start, name="start"),
]
