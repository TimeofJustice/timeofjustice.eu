"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import configparser
import os
import re
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

if os.name == 'nt':
    ROOT = '../'
else:
    ROOT = "/var/www/vue.timeofjustice.eu/"

CONFIG_FILE = ROOT + 'config.ini'

CONFIG_PARSER = configparser.ConfigParser(interpolation=None)
CONFIG_PARSER.read(CONFIG_FILE)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG_PARSER["DEFAULT"]["DJANGO_SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIG_PARSER["DEFAULT"].getboolean("DEBUG")
LOCAL_PRODUCTION = CONFIG_PARSER["DEFAULT"].getboolean("LOCAL_PRODUCTION")
PROPAGATE_EXCEPTIONS = True

ALLOWED_HOSTS = ['127.0.0.1',
                 'localhost',
                 'vue.timeofjustice.eu',]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_vite",
    "inertia",
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "inertia.middleware.InertiaMiddleware",
]

if LOCAL_PRODUCTION:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': CONFIG_PARSER["DEFAULT"]["SQL_DB"],
        'USER': CONFIG_PARSER["DEFAULT"]["SQL_USER"],
        'PASSWORD': CONFIG_PARSER["DEFAULT"]["SQL_PASS"],
        'HOST': 'localhost',
        'PORT': CONFIG_PARSER["DEFAULT"]["SQL_PORT"],
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# django-vite settings
# https://github.com/MrBin99/django-vite
DJANGO_VITE_DEV_MODE = DEBUG  # follow Django's dev mode

# Where ViteJS assets are built.
DJANGO_VITE_ASSETS_PATH = BASE_DIR / ".." / "frontend" / "dist"

# If use HMR or not. We follow Django's DEBUG mode
DJANGO_VITE_DEV_MODE = DEBUG

# Vite 3 defaults to 5173. Default for django-vite is 3000, which is the default for Vite 2.
DJANGO_VITE_DEV_SERVER_PORT = 5173


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Output directory for collectstatic to put all your static files into.
STATIC_ROOT = BASE_DIR / "staticfiles"

# Include DJANGO_VITE_ASSETS_PATH into STATICFILES_DIRS to be copied inside
# when run command python manage.py collectstatic
STATICFILES_DIRS = [DJANGO_VITE_ASSETS_PATH]

# Inertia settings
INERTIA_LAYOUT = BASE_DIR / "core" / "templates" / "index.html"

FILE_DESTINATION = CONFIG_PARSER["DEFAULT"]["FILE_DESTINATION"]

if LOCAL_PRODUCTION:
    # Vite generates files with 8 hash digits
    # http://whitenoise.evans.io/en/stable/django.html#WHITENOISE_IMMUTABLE_FILE_TEST
    def immutable_file_test(path, url):
        # Match filename with 12 hex digits before the extension
        # e.g. app.db8f2edc0c8a.js
        return re.match(r"^.+\.[0-9a-f]{8,12}\..+$", url)


    WHITENOISE_IMMUTABLE_FILE_TEST = immutable_file_test