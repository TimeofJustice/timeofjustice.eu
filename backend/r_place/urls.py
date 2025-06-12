from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("api/load_chunk/<int:x>/<int:y>/", views.load_chunk, name="load_chunk"),
    path("api/load_chunk/<int:x>/<int:y>/<int:size>/", views.load_chunk, name="load_chunk"),
    path("chat/", views.chat, name="chat"),
    path("<str:room_name>/", views.room, name="room"),
]
