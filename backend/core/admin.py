from django.contrib import admin
from modeltranslation.admin import TabbedExternalJqueryTranslationAdmin
from subadmin import RootSubAdmin, SubAdmin

from core.models import Image, Profile, Project, Social, Status, Technology, Tool


@admin.register(Profile)
class ProfileAdmin(TabbedExternalJqueryTranslationAdmin):
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
class SocialAdmin(TabbedExternalJqueryTranslationAdmin):
    list_display = ('id', 'icon', 'title', 'url')
    search_fields = ('title',)
    ordering = ('id',)


@admin.register(Status)
class StatusAdmin(TabbedExternalJqueryTranslationAdmin):
    list_display = ('order', 'name', 'color', 'id')
    search_fields = ('name',)
    ordering = ('order',)


class ImageSubAdmin(SubAdmin, TabbedExternalJqueryTranslationAdmin):
    model = Image
    list_display = ('id', 'project', 'image', 'alt')
    search_fields = ('alt',)
    ordering = ('id', 'project')


@admin.register(Project)
class ProjectAdmin(RootSubAdmin, TabbedExternalJqueryTranslationAdmin):
    list_display = ('id', 'title', 'status', 'description', 'short_description', 'github', 'webpage')
    search_fields = ('title', 'description', 'short_description', 'github')
    ordering = ('id',)

    subadmins = [ImageSubAdmin]
