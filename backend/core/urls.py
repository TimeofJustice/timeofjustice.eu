from django.urls import path

from .views import api, errors, helpers, pages

urlpatterns = [
    path("", pages.index, name="index"),
    path("project/<int:id>", pages.project_details, name="project_details"),
    path("error/<int:status_code>", pages.error, name="error"),

    path("api/project/<int:id>", api.project, name="project"),

    path("files/images/project/<str:name>", helpers.project_images, name="project_images"),
    path("files/images/lazy/project/<str:name>", helpers.project_images_lazy, name="project_images"),
    path("files/images/tool/<str:name>", helpers.tool_images, name="tool_images"),
    path("files/images/profile/<str:name>", helpers.profile_images, name="profile_images"),

    path("robots.txt", helpers.robot),
]