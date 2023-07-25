import datetime
import os
import PIL.Image
from django.db import models
import numpy
from PIL import Image as PILImage
from django.db.models.signals import post_delete
from django.dispatch import receiver


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
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    color = models.CharField(max_length=100)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=False)
    placed_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('x', 'y')

    def __str__(self):
        return f"{self.x} {self.y} {self.color} {self.last_modified}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        destination = 'home/jonas/timeofjustice.eu/timeofjustice/data/images/'

        if os.name == 'nt':
            destination = 'C:/xampp/htdocs/timeofjustice.eu/timeofjustice/static/data/images/'

        # the images are 100x100 find the correct image
        x = self.x - (self.x % 250)
        y = self.y - (self.y % 250)
        file_name = destination + f"{x}_{y}.png"

        if os.path.isfile(file_name):
            image = PILImage.open(file_name)
            image = image.convert("RGBA")
            image = image.resize((250, 250), PILImage.ANTIALIAS)
            data = numpy.array(image)

            date = datetime.datetime.fromtimestamp(os.path.getmtime(file_name))
            date = date - datetime.timedelta(hours=2)

            cells = Cell.objects.filter(
                x__gte=x,
                x__lte=x + 249,
                y__gte=y,
                y__lte=y + 249,
                last_modified__gte=date
            )
        else:
            image = PILImage.new('RGBA', (250, 250), (255, 255, 255, 0))
            data = numpy.array(image)

            cells = Cell.objects.filter(
                x__gte=x,
                x__lte=x + 249,
                y__gte=y,
                y__lte=y + 249
            )

        for cell in cells:
            data[cell.y - y][cell.x - x] = [int(cell.color[1:][i:i + 2], 16) for i in (0, 2, 4)] + [255]

        image = PILImage.fromarray(data)

        image.save(file_name)


@receiver(post_delete, sender=Cell)
def delete_hook(sender, instance, using, **kwargs):
    destination = 'home/jonas/timeofjustice.eu/timeofjustice/data/images/'

    if os.name == 'nt':
        destination = 'C:/xampp/htdocs/timeofjustice.eu/timeofjustice/static/data/images/'

    x = instance.x - (instance.x % 250)
    y = instance.y - (instance.y % 250)
    file_name = destination + f"{x}_{y}.png"

    image = PILImage.new('RGBA', (250, 250), (255, 255, 255, 0))
    data = numpy.array(image)

    cells = Cell.objects.filter(
        x__gte=x,
        x__lte=x + 249,
        y__gte=y,
        y__lte=y + 249
    )

    for cell in cells:
        data[cell.y - y][cell.x - x] = [int(cell.color[1:][i:i + 2], 16) for i in (0, 2, 4)] + [255]

    image = PILImage.fromarray(data)

    image.save(file_name)


class LastPlaced(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)


class PlaceTimeOut(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True, default=0)
    seconds = models.IntegerField(default=0)
