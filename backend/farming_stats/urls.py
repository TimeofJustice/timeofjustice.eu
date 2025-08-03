from django.urls import path

from farming_stats import views

urlpatterns = [
    path("", views.index, name="index"),
]
