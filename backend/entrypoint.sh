#!/bin/sh
set -e

echo "Creating locale directory..."
mkdir -p backend/locale

echo "Creating translation messages..."
python manage.py makemessages -l yoda

echo "Compiling translation messages..."
python manage.py compilemessages

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Supervisor..."
exec supervisord -n -c /etc/supervisor/conf.d/supervisord.conf