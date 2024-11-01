import os
import PIL.Image

from django.db import models

from django.conf import settings


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def generate_lazy_image(image, directory):
    img = PIL.Image.open(image)

    image_name = os.path.basename(image.path)
    image_path = settings.FILE_DESTINATION + f'images/lazy/{directory}/{image_name}'

    if not os.path.exists(os.path.dirname(image_path)):
        os.makedirs(os.path.dirname(image_path))

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

    image_name = os.path.basename(image.path)
    image_path = settings.FILE_DESTINATION + f'images/{directory}/{image_name}'

    width, height = img.size

    if width > size or height > size:
        h_coefficient = width/size
        target_height = height/h_coefficient

        img = img.resize((size, int(target_height)), PIL.Image.LANCZOS)

    img.save(image_path, quality=quality, optimize=True)
    img.close()


def lazy_image_to_json(image, base_url):
    return {
        'lazy': f"/files/images/lazy/{base_url}/{os.path.basename(image.file.name)}",
        'original': f"/files/images/{base_url}/{os.path.basename(image.file.name)}"
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
            'title_image': lazy_image_to_json(self.title_image, 'project') if self.title_image else None,
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            generate_lazy_image(self.image, 'project')
            compress(self.image, 'project', size=1080, quality=80)

    def json(self):
        return {
            'image': lazy_image_to_json(self.image, 'project'),
            'alt': {
                'de': self.alt_german,
                'en': self.alt_english,
                'yoda': self.alt_yoda
            }
        }
