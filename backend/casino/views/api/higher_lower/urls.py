from django.urls import path

from .api import start, higher, lower, draw, leave

urlpatterns = [
    path("start/<int:bet>", start, name="start"),

    path("higher/<str:session_id>", higher, name="higher"),
    path("draw/<str:session_id>", draw, name="draw"),
    path("lower/<str:session_id>", lower, name="lower"),

    path("leave/<str:session_id>", leave, name="leave"),
]
