from modeltranslation.translator import TranslationOptions, translator

from core import models


class ProfileTranslationOptions(TranslationOptions):
    fields = ('description', 'short_description')

translator.register(models.Profile, ProfileTranslationOptions)

class SocialTranslationOptions(TranslationOptions):
    fields = ('title',)

translator.register(models.Social, SocialTranslationOptions)

class StatusTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(models.Status, StatusTranslationOptions)

class ProjectTranslationOptions(TranslationOptions):
    fields = ('description', 'short_description', 'alt')

translator.register(models.Project, ProjectTranslationOptions)

class ImageTranslationOptions(TranslationOptions):
    fields = ('alt',)

translator.register(models.Image, ImageTranslationOptions)
