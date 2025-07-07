#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind unix:/sockets/gunicorn.sock backend.wsgi:application &
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
