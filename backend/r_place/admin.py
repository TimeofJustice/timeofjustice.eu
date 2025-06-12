from django.contrib import admin

# Register your models here.
from .models import Message, Cell

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "message")
    search_fields = ("room", "message")
    list_filter = ("room",)
    ordering = ("-id",)


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ("id", "x", "y", "color", "last_modified")
    search_fields = ("color",)
    list_filter = ("color",)
    ordering = ("-last_modified", "x", "y")
