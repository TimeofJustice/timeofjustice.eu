from django.contrib import admin

# Register your models here.
from .models import Technology, Project, Image, Status

admin.site.register(Technology)
admin.site.register(Project)
admin.site.register(Image)
admin.site.register(Status)
