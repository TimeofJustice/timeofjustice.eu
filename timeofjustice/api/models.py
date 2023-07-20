import os

import PIL.Image
from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ('name', )


class Status(models.Model):
    name = models.CharField(max_length=100)
    id = models.IntegerField(primary_key=True)

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        ordering = ('id', )


class Project(models.Model):
    name = models.CharField(max_length=100)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    languages = models.ManyToManyField(Tag)
    git = models.URLField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ('-name', )


class Image(models.Model):
    destination = 'home/jonas/timeofjustice.eu/timeofjustice/data/images/'

    if os.name == 'nt':
        destination = 'C:/xampp/htdocs/timeofjustice.eu/timeofjustice/static/data/images/'

    image = models.ImageField(upload_to=destination)
    preview = models.ImageField(upload_to=destination)
    alt = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    index = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.image}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = PIL.Image.open(self.preview)
        width, height = img.size
        target_width = 20
        h_coefficient = width/20
        target_height = height/h_coefficient
        img = img.resize((int(target_width), int(target_height)), PIL.Image.ANTIALIAS)
        img.save(self.preview.path, quality=100)
        img.close()
        self.preview.close()

    class Meta:
        ordering = ('index', )


class Cell(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    color = models.CharField(max_length=100)
