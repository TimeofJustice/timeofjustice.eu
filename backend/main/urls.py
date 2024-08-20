from django.urls import path, re_path
from . import views


app_name = "main"

urlpatterns = [
    path("robots.txt", views.robot),
    path("", views.index, name="index"),

    re_path(r'^(?:.*)/?$', views.index),
]
