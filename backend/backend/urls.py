"""
URL configuration for backend project.

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
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include
from django_otp.admin import OTPAdminSite
from django.conf import settings
from django.shortcuts import redirect

if not settings.DEBUG:
    admin.site.__class__ = OTPAdminSite

from . import settings

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("core.urls")),
    path("farming-stats/", include("farming_stats.urls")),
    path("games/", include("games.urls")),
    path("casino/", lambda request: redirect("/games/", permanent=False)),
]

handler404 = "core.views.errors.page_not_found"
handler500 = "core.views.errors.server_error"
handler403 = "core.views.errors.permission_denied"
handler400 = "core.views.errors.bad_request"
