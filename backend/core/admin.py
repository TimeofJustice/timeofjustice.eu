from django.contrib import admin

# Register your models here.
from .models import Technology, Project, Image, Status, Tool, Translation, Profile

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'text')
    list_filter = ('language',)
    search_fields = ('name', 'text')
    ordering = ('name', 'language')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'picture', 'description', 'short_description', 'repo')

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('id', 'icon', 'alt', 'url')
    search_fields = ('alt',)
    ordering = ('id',)

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'icon')
    search_fields = ('name',)
    ordering = ('id',)

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'color', 'id')
    search_fields = ('name',)
    ordering = ('order',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'description', 'short_description', 'github', 'webpage')
    search_fields = ('title', 'description', 'short_description', 'github')
    ordering = ('id',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'image', 'alt')
    search_fields = ('alt',)
    ordering = ('id', 'project',)
