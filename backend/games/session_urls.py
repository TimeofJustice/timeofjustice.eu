"""
Wallet session pages, mounted at the site root.

The wallet is no longer games-only, since r/place needs one too, so signing in
is not part of the games section any more.
"""

from django.urls import path

from games.views import pages

urlpatterns = [
    path("login/", pages.login, name="wallet_login"),
    path("register/", pages.register, name="wallet_register"),
    path("logout/", pages.logout, name="wallet_logout"),
]
