from django.contrib import admin

# Register your models here.
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "message")
    search_fields = ("room", "message")
    list_filter = ("room",)
    ordering = ("-id",)
