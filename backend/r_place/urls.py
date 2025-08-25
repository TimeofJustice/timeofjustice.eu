from django.urls import path

from r_place import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:canvas>/", views.index, name="index"),
    path("api/load/<str:canvas>/", views.load_canvas, name="load_canvas"),
]
