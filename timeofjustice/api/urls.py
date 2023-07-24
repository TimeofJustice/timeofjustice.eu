from django.urls import path, re_path
from . import views


app_name = "api"

urlpatterns = [
    path("api/project/<int:project_id>", views.project, name="project"),
    path("api/projects", views.projects_list, name="projects_list"),
    path("api/place/get", views.place_get),
    path("api/place/set", views.place_set),
    path("api/place/generate/<int:from_x>/<int:from_y>", views.gen),
    path("robots.txt", views.robot),
    path("", views.index, name="index"),
    re_path(r'^(?:.*)/?$', views.index),
]
