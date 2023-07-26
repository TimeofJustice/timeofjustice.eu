from django.urls import path, re_path
from . import views


app_name = "api"

urlpatterns = [
    path("api/project/<int:project_id>", views.get_project, name="project"),
    path("api/projects", views.projects_list, name="projects_list"),
    path("api/place/set", views.place_set),
    path("api/place/generate/<int:from_x>/<int:from_y>", views.gen),
    path("api/place/timeout", views.get_time_out),
    path("api/place/lastplaced", views.get_last_placed),
    path("api/place/export/<int:from_x>/<int:from_y>/<int:to_x>/<int:to_y>/<int:factor>", views.export),
    path("api/validate", views.validate_captcha),
    path("robots.txt", views.robot),
    path("", views.index, name="index"),
    re_path(r'^(?:.*)/?$', views.index),
]
