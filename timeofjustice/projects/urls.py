from django.urls import path

from . import views


app_name = "projects"
urlpatterns = [
    path("", views.index, name="index"),
    path("robot.txt", views.robot, name="robot"),
]