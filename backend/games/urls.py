from django.urls import include, path

from games.views import pages

urlpatterns = [
    path("", pages.index, name="index"),
    path("api/", include("games.views.core.urls")),
    path("api/higher-lower/", include("games.views.higher_lower.urls")),
    path("api/ride-the-bus/", include("games.views.ride_the_bus.urls")),
    path("api/black-jack/", include("games.views.black_jack.urls")),
    path("api/sic-bo/", include("games.views.sic_bo.urls")),
]
