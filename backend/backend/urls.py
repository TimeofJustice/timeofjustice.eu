"""URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django_otp.admin import OTPAdminSite
from django.urls import re_path

from r_place import consumers as r_place_consumers
from cards import consumers as cards_consumers

if os.getenv("USE_OTP", 'False').lower() in ('true', '1', 't'):
    admin.site.__class__ = OTPAdminSite

from backend import settings

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("core.urls")),
    path("games/", include("games.urls")),
    path("casino/", lambda request: redirect("/games/", permanent=False)),
    path("r-place/", include("r_place.urls")),
    path("sendy/", include("postcard.urls")),
    path("cards/", include("cards.urls")),
]

websocket_urlpatterns = [
    path("ws/r-place/", r_place_consumers.RPlaceConsumer.as_asgi()),
    path("ws/cards/", cards_consumers.RPlaceConsumer.as_asgi()),
]

handler400 = "core.views.errors.bad_request"
handler403 = "core.views.errors.permission_denied"
handler404 = "core.views.errors.page_not_found"
handler500 = "core.views.errors.server_error"
