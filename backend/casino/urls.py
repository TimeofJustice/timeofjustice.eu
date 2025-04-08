from django.urls import path

from .views import pages

urlpatterns = [
    path("", pages.index, name="index"),
    path("login/", pages.login, name="login"),
    path("register/", pages.register, name="register"),
    path("logout/", pages.logout, name="logout"),
    path("test/", pages.wallet_test, name="test"),
    path("api/higher-lower/start/<int:bet>", pages.higher_lower_start, name="higher_lower_start"),
    path("api/higher-lower/higher/<str:session_id>", pages.higher_lower_higher, name="higher_lower_higher"),
    path("api/higher-lower/lower/<str:session_id>", pages.higher_lower_lower, name="higher_lower_lower"),
    path("api/higher-lower/draw/<str:session_id>", pages.higher_lower_draw, name="higher_lower_draw"),
    path("api/higher-lower/leave/<str:session_id>", pages.higher_lower_leave, name="higher_lower_leave"),
]
