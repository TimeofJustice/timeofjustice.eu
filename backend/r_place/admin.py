from django.contrib import admin

# Register your models here.
from .models import Cell


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ("id", "x", "y", "color", "last_modified")
    search_fields = ("color",)
    list_filter = ("color",)
    ordering = ("-last_modified", "x", "y")
