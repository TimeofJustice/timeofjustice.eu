from django.urls import path

from habits import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:year>/", views.index, name="index_year"),
    path("api/year/<int:year>/", views.year, name="year"),
    path("api/habit/", views.create, name="create"),
    path("api/layout/", views.layout, name="layout"),
    path("api/habit/<int:habit_id>/", views.update, name="update"),
    path("api/habit/<int:habit_id>/delete/", views.delete, name="delete"),
    path("api/habit/<int:habit_id>/log/", views.log, name="log"),
]
