from django.urls import path, re_path
from .views import projects
from .views import place
from . import views


app_name = "api"

urlpatterns = [
    path("api/project/<int:project_id>", projects.get_project, name="project"),
    path("api/projects", projects.projects_list, name="projects_list"),

    path("api/place/timeout", place.get_time_out),
    path("api/place/lastplaced", place.get_last_placed),
    path("api/place/discover", place.discover),
    path("api/place/set", place.place_set),
    path("api/validate", place.validate_captcha),
    path("api/place/overlay/<str:overlay_name>", place.get_overlay),
    path("api/place/color/<int:x>/<int:y>", place.get_color),
    path("api/place/generate/<int:from_x>/<int:from_y>", place.gen),
    path("api/place/changes/<int:from_x>/<int:from_y>", place.changes),
    path("api/place/export/<int:from_x>/<int:from_y>/<int:to_x>/<int:to_y>/<int:factor>", place.export),

    path("robots.txt", views.robot),
    path("", projects.index, name="index"),

    re_path(r'^(?:.*)/?$', projects.index),
]
