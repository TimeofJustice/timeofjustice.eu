from django.urls import path

from quiz import views

urlpatterns = [
    path("", views.index, name="quiz_index"),
    path("join", views.join, name="quiz_join"),
    path("<str:lobby_code>", views.lobby, name="quiz_lobby_index"),
]
