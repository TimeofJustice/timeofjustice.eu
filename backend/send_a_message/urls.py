from django.urls import path

from send_a_message import views

urlpatterns = [
    path("", views.index, name="send_a_message_index"),
]
