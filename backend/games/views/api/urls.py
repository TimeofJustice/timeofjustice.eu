from django.urls import include, path

from .api import dismiss, leaderboard, redeem, update, vault

urlpatterns = [
    path("higher-lower/", include("games.views.api.higher_lower.urls")),
    path("ride-the-bus/", include("games.views.api.ride_the_bus.urls")),
    path("black-jack/", include("games.views.api.black_jack.urls")),
    path("sic-bo/", include("games.views.api.sic_bo.urls")),
    path("user/update/", update, name="update"),
    path("user/redeem/", redeem, name="redeem"),
    path("hint/dismiss/", dismiss, name="dismiss"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("vault/", vault, name="vault"),
]
