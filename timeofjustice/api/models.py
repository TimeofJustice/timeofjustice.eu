import datetime
import os
import PIL.Image
from django.conf import settings
from django.db import models
import numpy
from PIL import Image as PILImage
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from scipy.spatial import cKDTree
from sklearn.cluster import KMeans


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
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ('name', )
        verbose_name_plural = "1.0 Tags"


class Status(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        ordering = ('id', )
        verbose_name_plural = "1.1 Status"


class Project(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    languages = models.ManyToManyField(Tag)
    git = models.URLField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ('-name', )
        verbose_name_plural = "1.2 Projects"


class Image(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    image = models.ImageField(upload_to=settings.FILE_DESTINATION)
    preview = models.ImageField(upload_to=settings.FILE_DESTINATION)
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
        verbose_name_plural = "1.3 Images"


class Cell(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    color = models.CharField(max_length=100)
    last_modified = models.DateTimeField(editable=False)
    placed_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('x', 'y')
        verbose_name_plural = "2.0 Cells"

    def __str__(self):
        return f"{self.x} {self.y} {self.color} {self.last_modified}"

    def save(self, *args, **kwargs):
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)


@receiver(post_delete, sender=Cell)
def delete_hook(sender, instance, using, **kwargs):
    x = instance.x - (instance.x % 250)
    y = instance.y - (instance.y % 250)
    file_name = settings.FILE_DESTINATION + f"{x}_{y}.png"

    image = PILImage.new('RGBA', (250, 250), (255, 255, 255, 255))
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

    class Meta:
        verbose_name_plural = "2.1 Last Placed"


class PlaceTimeOut(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, default=0)
    seconds = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "2.2 Time-outs"


class Overlay(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "2.3 Overlays"


class OverlayImage(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, )
    image = models.ImageField(upload_to=settings.FILE_DESTINATION)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    width = models.IntegerField(default=50)
    height = models.IntegerField(default=50)
    overlay = models.ForeignKey(Overlay, on_delete=models.CASCADE, default=None)
    convert = models.BooleanField(default=False)
    max_colors = models.IntegerField(default=None, null=True)

    class Meta:
        verbose_name_plural = "2.4 Images"

    def image_name(self):
        return f"{self.image.name.split('/')[-1]}"
    image_name.short_description = 'Image'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = PIL.Image.open(self.image)
        img = img.convert("RGBA")

        original_width, original_height = img.size
        scale_factor = min(self.width / original_width, self.height / original_height)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        self.width = new_width
        self.height = new_height

        image = img.resize((new_width, new_height), PIL.Image.BICUBIC)

        if self.max_colors is not None:
            image_np = numpy.array(image)
            reshaped_image = numpy.reshape(image_np, (-1, image_np.shape[2]))

            model = KMeans(n_clusters=self.max_colors)
            labels = model.fit_predict(reshaped_image)
            palette = model.cluster_centers_

            quantized_raster = numpy.reshape(palette[labels], image_np.shape).astype(int)
            image = PILImage.fromarray(quantized_raster.astype('uint8'))

        name = "".join(os.path.basename(self.image.name).split(".")[0:-1])
        png_name = f'{name}_norm.png'
        png_path = settings.FILE_DESTINATION + png_name
        image.save(png_path)

        im_matrix = numpy.array(image)

        image_lay = PIL.Image.new('RGBA', (new_width * 3, new_height * 3), (255, 255, 255, 0))
        data = numpy.array(image_lay)

        if self.convert:
            color_array = numpy.array([hex_to_rgb(hex_code) for hex_code in hex_color_palette])

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
        img.close()
        self.image.close()

        name = "".join(os.path.basename(self.image.name).split(".")[0:-1])

        png_name = f'{name}.png'
        png_path = settings.FILE_DESTINATION + png_name
        fin_image.save(png_path, quality=100)

        self.image = png_path

        super().save(*args, **kwargs)
