from django.urls import path

from games.views.black_jack.api import hit, stand, start

urlpatterns = [
    path("start/", start, name="start"),

    path("hit/", hit, name="hit"),
    path("stand/", stand, name="stand"),
]
