from django.contrib import admin

from r_place.models import Canvas, Cell, RenderedCanvas


@admin.register(Canvas)
class CanvasAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "width", "height", "active")
    search_fields = ("name",)
    list_filter = ("active",)
    ordering = ("-id", "name")
    readonly_fields = ("id",)


@admin.register(RenderedCanvas)
class RenderedCanvasAdmin(admin.ModelAdmin):
    list_display = ("id", "canvas", "image_name", "created_at")
    search_fields = ("canvas__name", "image_name")
    list_filter = ("canvas__name",)
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at")


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ("id", "x", "y", "color", "last_modified", "canvas")
    search_fields = ("color", "x", "y", "canvas__name")
    list_filter = ("color", "canvas__name")
    ordering = ("-last_modified", "x", "y", "canvas__active")
