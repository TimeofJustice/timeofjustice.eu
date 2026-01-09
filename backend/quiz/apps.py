import sys

from django.apps import AppConfig


class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz'

    def ready(self):
        if "runserver" not in sys.argv and "/usr/local/bin/gunicorn" not in sys.argv:
            return

        from quiz.tasks import tick_all_sessions

        tick_all_sessions(repeat=10, schedule=10, remove_existing_tasks=True)
