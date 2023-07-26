from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Project)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'languages', 'git', 'description']
    search_fields = ['name']


@admin.register(models.Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(models.PlaceTimeOut)
class PlaceTimeOutAdmin(admin.ModelAdmin):
    list_display = ['seconds']
    search_fields = ['id']


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'preview', 'alt', 'project', 'index')
    search_fields = ['project']
    list_filter = ['project']


@admin.register(models.LastPlaced)
class LastPlacedAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp')
    search_fields = ['id']


@admin.register(models.Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ('x', 'y', 'color', 'last_modified', 'placed_by')
    search_fields = ['x', 'y']
    list_filter = ('x', 'y', 'color', 'last_modified')
