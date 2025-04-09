from django.urls import path

from .api import start, red, black, higher, lower, inside, outside, hearts, clubs, diamonds, spades, leave

urlpatterns = [
    path("start/<int:bet>", start, name="start"),
    path("red/<str:session_id>", red, name="red"),
    path("black/<str:session_id>", black, name="black"),
    path("higher/<str:session_id>", higher, name="higher"),
    path("lower/<str:session_id>", lower, name="lower"),
    path("inside/<str:session_id>", inside, name="inside"),
    path("outside/<str:session_id>", outside, name="outside"),
    path("hearts/<str:session_id>", hearts, name="hearts"),
    path("clubs/<str:session_id>", clubs, name="clubs"),
    path("diamonds/<str:session_id>", diamonds, name="diamonds"),
    path("spades/<str:session_id>", spades, name="spades"),
    path("leave/<str:session_id>", leave, name="leave"),
]
