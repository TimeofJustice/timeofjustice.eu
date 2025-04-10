from django.urls import path

from .api import start, red, black, higher, lower, inside, outside, hearts, clubs, diamonds, spades, leave

urlpatterns = [
    path("start/", start, name="start"),

    path("red/", red, name="red"),
    path("black/", black, name="black"),

    path("higher/", higher, name="higher"),
    path("lower/", lower, name="lower"),

    path("inside/", inside, name="inside"),
    path("outside/", outside, name="outside"),

    path("hearts/", hearts, name="hearts"),
    path("clubs/", clubs, name="clubs"),
    path("diamonds/", diamonds, name="diamonds"),
    path("spades/", spades, name="spades"),

    path("leave/", leave, name="leave"),
]
