from django.contrib import admin

from core.models import Image, Profile, Project, Social, Status, Technology, Tool, Translation


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

@admin.register(Social)
class SocialAdmin(admin.ModelAdmin):
    list_display = ('id', 'icon', 'title', 'url')
    search_fields = ('title',)
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
    ordering = ('id', 'project')
