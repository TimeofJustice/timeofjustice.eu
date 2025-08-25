from django.urls import path

from core.views import api, helpers, pages

urlpatterns = [
    path("", pages.index, name="projects"),
    path("projects/<int:project_id>", pages.project_details, name="project_details"),
    path("error/<int:status_code>", pages.error, name="error"),

    path("api/project/<int:project_id>", api.project, name="project"),

    # Serving static files in development
    path("files/global/favicon/<str:name>", helpers.favicon_images, name="favicon_images"),
    path("files/images/project/<str:name>", helpers.project_images, name="project_images"),
    path("files/images/lazy/project/<str:name>", helpers.project_images_lazy, name="project_images"),
    path("files/images/tool/<str:name>", helpers.tool_images, name="tool_images"),
    path("files/images/profile/<str:name>", helpers.profile_images, name="profile_images"),
    path("files/video/project/<str:name>", helpers.project_video, name="project_video"),
    path("files/images/games/cards/<str:name>", helpers.games_cards, name="games_cards"),
    path("files/images/r-place/<str:name>", helpers.r_place_images, name="r_place_images"),

    path("robots.txt", helpers.robot),
]
