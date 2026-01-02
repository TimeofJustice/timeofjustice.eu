from django.urls import path

from quiz import views

urlpatterns = [
    path("", views.index, name="quiz_index"),
    path("<str:lobby_code>", views.lobby, name="quiz_lobby_index"),
]
