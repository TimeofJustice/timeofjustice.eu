from django.contrib import admin
from . import models


# Register your models here.
admin.site.register(models.Project)
admin.site.register(models.Status)
admin.site.register(models.Tag)
admin.site.register(models.Image)
admin.site.register(models.PlaceTimeOut)

@admin.register(models.Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ('x', 'y', 'color', 'last_modified', 'placed_by')
    search_fields = ['x', 'y']
    list_filter = ('x', 'y', 'color', 'last_modified')
