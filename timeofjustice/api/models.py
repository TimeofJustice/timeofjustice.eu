import datetime
import os
import PIL.Image
import numpy as np
from django.db import models
import numpy
from PIL import Image as PILImage
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from scipy.spatial import cKDTree


def hex_to_rgb(hex_code):
    # Hex-Code in RGB-Tupel umwandeln
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


def find_nearest_color(color_array, target_color):
    tree = cKDTree(color_array)
    _, index = tree.query(target_color[:3])
    return color_array[index]


hex_color_palette = [
    '#6D001A',
    '#FF4500',
    '#FFD635',
    '#00A368',
    '#7EED56',
    '#009EAA',
    '#2450A4',
    '#51E9F4',
    '#6A5CFF',
    '#811E9F',
    '#E4ABFF',
    '#FF3881',
    '#6D482F',
    '#FFB470',
    '#515252',
    '#D4D7D9',
    '#BE0039',
    '#FFA800',
    '#FFF8B8',
    '#00CC78',
    '#00756F',
    '#00CCC0',
    '#3690EA',
    '#493AC1',
    '#94B3FF',
    '#B44AC0',
    '#DE107F',
    '#FF99AA',
    '#9C6926',
    '#000000',
    '#898D90',
    '#FFFFFF'
]


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

    def image_name(self):
        return f"{self.image.name.split('/')[-1]}"
    image_name.short_description = 'Image'

    def preview_name(self):
        return f"{self.preview.name.split('/')[-1]}"
    preview_name.short_description = 'Preview'

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
    last_modified = models.DateTimeField(auto_now=True)
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
            date = timezone.make_aware(date)

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
    timestamp = models.DateTimeField(default=timezone.now)


class PlaceTimeOut(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True, default=0)
    seconds = models.IntegerField(default=0)


class Overlay(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=255)


class OverlayImage(models.Model):
    destination = 'home/jonas/timeofjustice.eu/timeofjustice/data/images/'

    if os.name == 'nt':
        destination = 'C:/xampp/htdocs/timeofjustice.eu/timeofjustice/static/data/images/'

    id = models.IntegerField(primary_key=True, auto_created=True)
    image = models.ImageField(upload_to=destination)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    width = models.IntegerField(default=50)
    height = models.IntegerField(default=50)
    overlay = models.ForeignKey(Overlay, on_delete=models.CASCADE, default=None)
    convert = models.BooleanField(default=False)

    def image_name(self):
        return f"{self.image.name.split('/')[-1]}"
    image_name.short_description = 'Image'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = PIL.Image.open(self.image)

        original_width, original_height = img.size
        aspect_ratio = original_width / original_height
        scale_factor = min(self.width / original_width, self.height / original_height)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        self.width = new_width
        self.height = new_height

        image = img.resize((new_width, new_height), PIL.Image.BICUBIC)
        im_matrix = numpy.array(image)

        imageLay = PIL.Image.new('RGBA', (new_width * 3, new_height * 3), (255, 255, 255, 0))
        data = numpy.array(imageLay)

        if self.convert:
            color_array = np.array([hex_to_rgb(hex_code) for hex_code in hex_color_palette])

            for y in range(new_height):
                for x in range(new_width):
                    pixel = image.getpixel((x, y))

                    if pixel[3] != 0:
                        nearest_color = find_nearest_color(color_array, pixel)
                        im_matrix[y][x] = [nearest_color[0], nearest_color[1], nearest_color[2], 255]

        for i in range(0, new_width):
            for j in range(0, new_height):
                data[j * 3 + 1][i * 3 + 1] = im_matrix[j][i]

                if im_matrix[j][i][3] != 0:
                    data[j * 3 + 1][i * 3 + 1][3] = 255

        fin_image = PIL.Image.fromarray(data)
        fin_image.save(self.image.path, quality=100)
        img.close()
        self.image.close()
        super().save(*args, **kwargs)
