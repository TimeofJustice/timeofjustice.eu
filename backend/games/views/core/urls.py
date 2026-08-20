from django.urls import path

from games.views.core.api import avatars, leaderboard, redeem, update, vault, wallet_phrase

urlpatterns = [
    path("user/update/", update, name="update"),
    path("user/avatars/", avatars, name="avatars"),
    path("user/wallet-phrase/", wallet_phrase, name="wallet_phrase"),
    path("user/redeem/", redeem, name="redeem"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("vault/", vault, name="vault"),
]
