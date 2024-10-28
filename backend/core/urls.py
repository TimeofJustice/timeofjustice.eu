from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/project/<int:id>", views.project, name="project"),
]