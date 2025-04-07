from django.urls import path

from .views import pages

urlpatterns = [
    path("", pages.index, name="index"),
    path("login/", pages.login, name="login"),
    path("register/", pages.register, name="register"),
    path("test/", pages.wallet_test, name="test"),
]
