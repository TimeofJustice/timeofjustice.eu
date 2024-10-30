import os

from django.db import models

from django.conf import settings


class Technology(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    icon = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return self.name

    def json(self):
        return {
            'name': self.name,
            'icon': self.icon
        }


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)

    short_description_german = models.TextField(max_length=100, null=True, blank=True)
    short_description_english = models.TextField(max_length=100, null=True, blank=True)
    short_description_yoda = models.TextField(max_length=100, null=True, blank=True)

    description_german = models.TextField(null=True, blank=True)
    description_english = models.TextField(null=True, blank=True)
    description_yoda = models.TextField(null=True, blank=True)

    technology = models.ManyToManyField('Technology', blank=True)

    title_image = models.ImageField(upload_to=settings.FILE_DESTINATION + 'images/project/')
    alt_german = models.TextField(max_length=100, null=True, blank=True)
    alt_english = models.TextField(max_length=100, null=True, blank=True)
    alt_yoda = models.TextField(max_length=100, null=True, blank=True)

    github = models.URLField(max_length=100, null=True, blank=True)
    webpage = models.URLField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.title

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'short_description': {
                'de': self.short_description_german,
                'en': self.short_description_english,
                'yoda': self.short_description_yoda
            },
            'description': {
                'de': self.description_german,
                'en': self.description_english,
                'yoda': self.description_yoda
            },
            'technologies': [tech.json() for tech in self.technology.all()],
            'title_image': f"/files/images/project/{os.path.basename(self.title_image.file.name)}",
            'alt': {
                'de': self.alt_german,
                'en': self.alt_english,
                'yoda': self.alt_yoda
            },
            'github': self.github,
            'webpage': self.webpage
        }


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=settings.FILE_DESTINATION + 'images/project/')
    alt_german = models.TextField(max_length=100, null=True, blank=True)
    alt_english = models.TextField(max_length=100, null=True, blank=True)
    alt_yoda = models.TextField(max_length=100, null=True, blank=True)

    def json(self):
        return {
            'image': f"/files/images/project/{os.path.basename(self.image.file.name)}",
            'alt': {
                'de': self.alt_german,
                'en': self.alt_english,
                'yoda': self.alt_yoda
            }
        }
