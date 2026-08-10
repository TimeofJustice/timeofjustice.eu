from django.contrib import admin
from subadmin import RootSubAdmin, SubAdmin

from quiz.models import Player, PlayerGIF, Session


class PlayerAdmin(SubAdmin):
    model = Player
    list_display = ('id',)


@admin.register(Session)
class QuizSessionAdmin(RootSubAdmin):
    list_display = ('id', 'max_players', 'is_active', 'created_at')

    subadmins = [PlayerAdmin]


@admin.register(PlayerGIF)
class PlayerGIFAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
