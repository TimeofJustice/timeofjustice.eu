from django.contrib import admin

from quiz.models import QuizSession


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'host_id', 'max_players', 'time_per_question', 'mode', 'is_active', 'created_at')
