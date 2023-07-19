from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Project)
admin.site.register(models.Status)
admin.site.register(models.Tag)
admin.site.register(models.Image)
