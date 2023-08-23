from django.contrib import admin
from django.utils import timezone
from rangefilter.filters import NumericRangeFilterBuilder

from . import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'tags_list', 'git', 'description']
    search_fields = ['name']
    list_filter = ["status", "tags"]


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_name', 'alt', 'project', 'index')
    search_fields = ['project', 'image_name', 'alt']
    list_filter = ['project']


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_placed', 'valid_until')
    search_fields = ['id']
    list_filter = ['last_placed', 'valid_until']


@admin.action(description="Censor the selected pixels")
def censor(modeladmin, request, queryset):
    queryset.update(color="#FFFFFF", last_modified=timezone.now())


@admin.register(models.Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ('id', 'x', 'y', 'color', 'last_modified', 'placed_by')
    search_fields = ['placed_by']
    list_filter = (
        ('x', NumericRangeFilterBuilder()),
        ('y', NumericRangeFilterBuilder()),
        'last_modified', 'placed_by'
    )
    actions = [censor]


@admin.register(models.PlaceTimeOut)
class PlaceTimeOutAdmin(admin.ModelAdmin):
    list_display = ['id', 'seconds']
    search_fields = ['id']


@admin.register(models.Overlay)
class OverlayAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.OverlayImage)
class OverlayImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_name', 'overlay', 'x', 'y', 'width', 'height', 'convert', 'max_colors']
    search_fields = ['image_name']
    list_filter = ['overlay', 'x', 'y', 'width', 'height', 'convert']


@admin.register(models.Tile)
class TileAdmin(admin.ModelAdmin):
    list_display = ['id', 'x', 'y', 'last_updated']
    list_filter = ['x', 'y', 'last_updated']
