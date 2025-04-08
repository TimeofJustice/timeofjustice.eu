from django.urls import path, include

from .views import pages

urlpatterns = [
    path("", pages.index, name="index"),
    path("login/", pages.login, name="login"),
    path("register/", pages.register, name="register"),
    path("logout/", pages.logout, name="logout"),

    path("api/", include("casino.views.api.urls")),
]
