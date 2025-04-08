from django.urls import path, include

urlpatterns = [
    path("higher-lower/", include("casino.views.api.higher_lower.urls")),
]
