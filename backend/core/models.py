from pathlib import Path

import PIL.Image
from django.conf import settings
from django.db import models

from core.helpers import get_or_none


def generate_lazy_image(image, directory):
    img = PIL.Image.open(image)

    image_name = Path(image.path).name
    image_path =  f'{settings.FILE_DESTINATION}images/lazy/{directory}/{image_name}'

    if not Path(Path(image_path).parent).exists():
        Path(image_path).parent.mkdir(parents=True, exist_ok=True)

    width, height = img.size
    target_width = 100
    h_coefficient = width/100
    target_height = height/h_coefficient

    img = img.resize((int(target_width), int(target_height)), PIL.Image.LANCZOS)
    img.save(image_path, quality=100)
    img.close()

    return image_path


def compress(image, directory, size=480, quality=50):
    img = PIL.Image.open(image)

    image_name = Path(image.path).name
    image_path = f'{settings.FILE_DESTINATION}images/{directory}/{image_name}'

    width, height = img.size

    if width > size or height > size:
        h_coefficient = width/size
        target_height = height/h_coefficient

        img = img.resize((size, int(target_height)), PIL.Image.LANCZOS)

    img.save(image_path, quality=quality, optimize=True)
    img.close()


def lazy_image_to_json(image, base_url):
    return {
        'lazy': f"/{settings.FILE_DESTINATION}images/lazy/{base_url}/{Path(image.file.name).name}",
        'original': f"/{settings.FILE_DESTINATION}images/{base_url}/{Path(image.file.name).name}",
    }


class Translation(models.Model):
    name = models.CharField(max_length=100)
    language = models.CharField(max_length=4)
    text = models.TextField()

    def __str__(self):
        return self.text

    class Meta:
        unique_together = ('name', 'language')
        ordering = ('name',)


def get_translation(name):
    de = get_or_none(Translation, name=name, language='de')
    en = get_or_none(Translation, name=name, language='en')
    yoda = get_or_none(Translation, name=name, language='yoda')

    fallback = en.text if en is not None else (name if name is not None else "")

    return {
        'de': de.text if de is not None else fallback,
        'en': en.text if en is not None else fallback,
        'yoda': yoda.text if yoda is not None else fallback,
    }


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ImageField(upload_to=f'{settings.FILE_DESTINATION}images/profile/', max_length=1000, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    short_description = models.CharField(max_length=100, null=True, blank=True)
    repo = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.short_description

    def json(self):
        return {
            'picture': f"/{settings.FILE_DESTINATION}images/profile/{Path(self.picture.file.name).name}" if self.picture else None,
            'description': get_translation(self.description),
            'short_description': get_translation(self.short_description),
            'repository': self.repo if self.repo else None,
        }


class Tool(models.Model):
    id = models.AutoField(primary_key=True)
    icon = models.FileField(upload_to=f'{settings.FILE_DESTINATION}images/tool/', max_length=1000)
    alt = models.CharField(max_length=20, null=True, blank=True)
    url = models.URLField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.alt

    def json(self):
        return {
            'icon': f"/{settings.FILE_DESTINATION}images/tool/{Path(self.icon.file.name).name}" if self.icon else None,
            'alt': self.alt,
            'url': self.url,
        }


class Technology(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    icon = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return self.name

    def json(self):
        return {
            'name': self.name,
            'icon': self.icon,
        }


class Status(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name if self.name else ""

    def json(self):
        return {
            'name': get_translation(self.name),
            'color': self.color,
        }


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    status = models.ForeignKey('Status', on_delete=models.CASCADE, null=True, blank=True)
    short_description = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    technology = models.ManyToManyField('Technology', blank=True)
    title_image = models.ImageField(upload_to=f'{settings.FILE_DESTINATION}images/project/', null=True, blank=True, max_length=1000)
    alt = models.CharField(max_length=100, null=True, blank=True)
    github = models.URLField(max_length=100, null=True, blank=True)
    webpage = models.URLField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.title_image:
            generate_lazy_image(self.title_image, 'project')
            compress(self.title_image, 'project')

    class Meta:
        ordering = ['status']

    def __str__(self):
        return self.title

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'status': self.status.json() if self.status else None,
            'short_description': get_translation(self.short_description),
            'description': get_translation(self.description),
            'technologies': [tech.json() for tech in self.technology.all()],
            'title_image': lazy_image_to_json(self.title_image, 'project') if self.title_image else None,
            'alt': get_translation(self.alt),
            'github': self.github,
            'website': self.webpage,
            'images': [image.json() for image in Image.objects.filter(project=self)],
        }


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=f'{settings.FILE_DESTINATION}images/project/', max_length=1000, null=True, blank=True)
    video = models.FileField(upload_to=f'{settings.FILE_DESTINATION}video/project/', max_length=1000, null=True, blank=True)
    alt = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.alt if self.alt else ""

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            generate_lazy_image(self.image, 'project')
            compress(self.image, 'project', size=1080, quality=80)

    def json(self):
        return {
            'image': lazy_image_to_json(self.image, 'project') if self.image else None,
            'video': f"/{settings.FILE_DESTINATION}video/project/{Path(self.video.file.name).name}" if self.video else None,
            'alt': get_translation(self.alt),
        }
