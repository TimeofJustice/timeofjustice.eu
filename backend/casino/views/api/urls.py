from django.urls import path, include

from .user import update, redeem, leaderboard

urlpatterns = [
    path("higher-lower/", include("casino.views.api.higher_lower.urls")),
    path("ride-the-bus/", include("casino.views.api.ride_the_bus.urls")),
    path("user/update/", update, name="update"),
    path("user/redeem/", redeem, name="redeem"),
    path("leaderboard/", leaderboard, name="leaderboard"),
]
