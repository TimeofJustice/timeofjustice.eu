from django.urls import path, include

urlpatterns = [
    path("higher-lower/", include("casino.views.api.higher_lower.urls")),
    path("ride-the-bus/", include("casino.views.api.ride_the_bus.urls")),
]
