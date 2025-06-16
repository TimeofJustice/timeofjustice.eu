from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:canvas>/", views.index, name="index"),
    path("api/load_chunk/<int:x>/<int:y>/<str:canvas>/", views.load_chunk, name="load_chunk"),
    path("api/load_chunk/<int:x>/<int:y>/<int:size>/<str:canvas>/", views.load_chunk, name="load_chunk"),
]
