from django.urls import path

from games.views.core.api import avatars, dismiss, leaderboard, redeem, update, vault

urlpatterns = [
    path("user/update/", update, name="update"),
    path("user/avatars/", avatars, name="avatars"),
    path("user/redeem/", redeem, name="redeem"),
    path("hint/dismiss/", dismiss, name="dismiss"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("vault/", vault, name="vault"),
]
