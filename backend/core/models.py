import os

from django.db import models

from django.conf import settings


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


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


class Status(models.Model):
    id = models.AutoField(primary_key=True)
    name_german = models.CharField(max_length=20)
    name_english = models.CharField(max_length=20)
    name_yoda = models.CharField(max_length=20)
    color = models.CharField(max_length=20, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name_german

    def json(self):
        return {
            'name': {
                'de': self.name_german,
                'en': self.name_english,
                'yoda': self.name_yoda
            },
            'color': self.color
        }


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)

    status = models.ForeignKey('Status', on_delete=models.CASCADE, null=True, blank=True)

    short_description_german = models.TextField(max_length=100, null=True, blank=True)
    short_description_english = models.TextField(max_length=100, null=True, blank=True)
    short_description_yoda = models.TextField(max_length=100, null=True, blank=True)

    description_german = models.TextField(null=True, blank=True)
    description_english = models.TextField(null=True, blank=True)
    description_yoda = models.TextField(null=True, blank=True)

    technology = models.ManyToManyField('Technology', blank=True)

    title_image = models.ImageField(upload_to=settings.FILE_DESTINATION + 'images/project/', null=True, blank=True)
    alt_german = models.TextField(max_length=100, null=True, blank=True)
    alt_english = models.TextField(max_length=100, null=True, blank=True)
    alt_yoda = models.TextField(max_length=100, null=True, blank=True)

    github = models.URLField(max_length=100, null=True, blank=True)
    webpage = models.URLField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['status']

    def __str__(self):
        return self.title

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'status': self.status.json() if self.status else None,
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
            'title_image': f"/files/images/project/{os.path.basename(self.title_image.file.name)}" if self.title_image else None,
            'alt': {
                'de': self.alt_german,
                'en': self.alt_english,
                'yoda': self.alt_yoda
            },
            'github': self.github,
            'webpage': self.webpage,
            'images': [image.json() for image in Image.objects.filter(project=self)]
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
