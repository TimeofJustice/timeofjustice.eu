"""
Django settings for timeofjustice project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import configparser
import json
import os
from pathlib import Path

from django_ratelimit.decorators import ratelimit

if os.name == 'nt':
    ROOT = "./"
else:
    ROOT = "/var/www/timeofjustice.eu/"

CONFIG_FILE = ROOT + 'config.ini'

CONFIG_PARSER = configparser.ConfigParser(interpolation=None)
CONFIG_PARSER.read(CONFIG_FILE)

FILE_DESTINATION = CONFIG_PARSER["DEFAULT"]["IMAGE_DEST"]

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG_PARSER["DEFAULT"]["DJANGO_SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIG_PARSER["DEFAULT"].getboolean("DEBUG")
# Show error messages in production
DEBUG_PROPAGATE_EXCEPTIONS = True

TIME_ZONE = 'UTC'
USE_TZ = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'vue.timeofjustice.eu',
]
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'http://127.0.0.1',
    'http://localhost',
    'https://vue.timeofjustice.eu'
]
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1',
    'http://localhost',
    'https://vue.timeofjustice.eu'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'main',
    'corsheaders',
    'rangefilter',
]

MIDDLEWARE = [
    'main.middleware.reverse_proxy',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware'
]

RATELIMIT_VIEW = 'main.views.ratelimited_error'

ROOT_URLCONF = 'timeofjustice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            CONFIG_PARSER["DEFAULT"]["TEMPLATE_DIR"]
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'timeofjustice.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': CONFIG_PARSER["DEFAULT"]["SQL_DB"],
        'USER': CONFIG_PARSER["DEFAULT"]["SQL_USER"],
        'PASSWORD': CONFIG_PARSER["DEFAULT"]["SQL_PASS"],
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'sql_mode': 'STRICT_ALL_TABLES',
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "data/dist/static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "data/static")

if DEBUG:
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
