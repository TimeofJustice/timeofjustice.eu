from django.urls import path

from postcard import views

urlpatterns = [
    path("", views.index, name="postcard_index"),
    path("<str:postcard_id>", views.index, name="postcard_index"),
    path("api/send/", views.send_postcard, name="postcard_send"),
    path("api/report/<str:postcard_id>", views.report_postcard, name="postcard_report"),
]
