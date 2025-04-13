from django.urls import path

from .api import start, process_turn

urlpatterns = [
    path("start/", start, name="start"),
    path("<str:turn>/", process_turn, name="process_turn"),
]
