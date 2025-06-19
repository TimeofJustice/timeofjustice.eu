#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 backend.wsgi:application &
daphne -b 0.0.0.0 -p 8001 backend.asgi:application
