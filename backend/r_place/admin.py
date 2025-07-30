from django.contrib import admin

# Register your models here.
from .models import Canvas, Cell


@admin.register(Canvas)
class CanvasAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "width", "height", "active")
    search_fields = ("name",)
    list_filter = ("active",)
    ordering = ("-id", "name")
    readonly_fields = ("id",)


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ("id", "x", "y", "color", "last_modified", "canvas")
    search_fields = ("color", "x", "y", "canvas__name")
    list_filter = ("color", "canvas__name")
    ordering = ("-last_modified", "x", "y", "canvas__active")
