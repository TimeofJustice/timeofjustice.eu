from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("project/<int:id>", views.project_details, name="project_details"),
    path("api/project/<int:id>", views.project, name="project"),
    path("files/images/project/<str:name>", views.project_images, name="project_images"),
    path("files/images/lazy/project/<str:name>", views.project_images_lazy, name="project_images"),
    path("error/<int:status_code>", views.error, name="error"),
    path("robots.txt", views.robot),
]