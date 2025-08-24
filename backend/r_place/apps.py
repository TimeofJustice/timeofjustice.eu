import sys

from django.apps import AppConfig


class RPlaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'r_place'

    def ready(self):
        if "runserver" not in sys.argv and "/usr/local/bin/gunicorn" not in sys.argv:
            return

        from r_place.tasks import render_canvas

        render_canvas(repeat=60 * 60, schedule=60)
