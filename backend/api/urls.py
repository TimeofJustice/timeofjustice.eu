from django.urls import path, re_path
from .views import projects
from .views import place


app_name = "api"

urlpatterns = [
    path("project/<int:project_id>", projects.get_project, name="project"),
    path("projects", projects.projects_list, name="projects_list"),

    path("place/timeout", place.get_time_out),
    path("place/lastplaced", place.get_last_placed),
    path("place/discover", place.discover),
    path("place/set", place.place_set),
    path("validate", place.validate_captcha),
    path("place/overlay/<str:overlay_name>", place.get_overlay),
    path("place/overlay/<str:overlay_name>/<int:index>/<str:color>", place.get_overlay_color),
    path("place/color/<int:x>/<int:y>", place.get_color),
    path("place/generate/<int:from_x>/<int:from_y>", place.gen),
    path("place/changes/<int:from_x>/<int:from_y>", place.changes),
    path("place/export/<int:from_x>/<int:from_y>/<int:to_x>/<int:to_y>/<int:factor>", place.export),
]
