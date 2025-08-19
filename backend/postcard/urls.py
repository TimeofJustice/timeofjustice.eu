from django.urls import path

from postcard import views

urlpatterns = [
    path("", views.index, name="postcard_index"),
    path("<str:postcard_id>", views.index, name="postcard_index"),
]
