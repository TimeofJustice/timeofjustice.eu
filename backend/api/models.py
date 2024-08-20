import os
import PIL.Image
from django.conf import settings
from django.db import models
import numpy
from PIL import Image as PILImage
from django.utils import timezone
from sklearn.cluster import KMeans

from .helpers import hex_to_rgb, find_nearest_color

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
        return f"{self.name} ({self.id})"

    class Meta:
        ordering = ('name', )
        verbose_name = " Tag"
        verbose_name_plural = " Tags"


class Status(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        ordering = ('id', )
        verbose_name = " Status"
        verbose_name_plural = " Status"


class Project(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    git = models.URLField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.id})"

    def tags_list(self):
        tags = [str(tag) for tag in self.tags.all()]

        return tags
    tags_list.short_description = 'Tags'

    class Meta:
        ordering = ('-name', )
        verbose_name = " Project"
        verbose_name_plural = " Projects"


class Image(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    image = models.ImageField(upload_to=settings.FILE_DESTINATION + "projects/", max_length=255)
    preview = models.ImageField(editable=False, null=True, max_length=255)
    alt = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    index = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.image}"

    def image_name(self):
        return f"{self.image.name.split('/')[-1]}"
    image_name.short_description = 'Image'

    def save(self, *args, **kwargs):
        img = PIL.Image.open(self.image)

        image_name = os.path.basename(self.image.path)
        image_path = settings.FILE_DESTINATION + f"projects/previews/{image_name}"

        width, height = img.size
        target_width = 20
        h_coefficient = width/20
        target_height = height/h_coefficient

        img = img.resize((int(target_width), int(target_height)), PIL.Image.ANTIALIAS)
        img.save(image_path, quality=100)
        img.close()

        self.preview = image_path
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('project', 'index', )
        verbose_name = " Image"
        verbose_name_plural = " Images"


class Session(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    last_placed = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-last_placed', )
        verbose_name = "  Session"
        verbose_name_plural = "  Sessions"

    def __str__(self):
        return f"{self.id} ({self.valid_until})"


class Cell(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    color = models.CharField(max_length=7)
    last_modified = models.DateTimeField(editable=False)
    placed_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('-last_modified', 'x', 'y')
        verbose_name = "  Cell"
        verbose_name_plural = "  Cells"

    def __str__(self):
        return f"{self.color} ({self.x}, {self.y})"

    def save(self, *args, **kwargs):
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)


class PlaceTimeOut(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, default=0)
    seconds = models.IntegerField(default=0)

    class Meta:
        verbose_name = "  Time-out"
        verbose_name_plural = "  Time-outs"

    def __str__(self):
        return f"{self.seconds} ({self.id})"


class Overlay(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=10)

    class Meta:
        verbose_name = "  Overlay"
        verbose_name_plural = "  Overlays"

    def __str__(self):
        return f"{self.name} ({self.id})"


class OverlayImage(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    image = models.ImageField(upload_to=settings.FILE_DESTINATION + "layouts/originals", max_length=255)
    layout = models.ImageField(editable=False, null=True, max_length=255)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    width = models.IntegerField(default=50)
    height = models.IntegerField(default=50)
    overlay = models.ForeignKey(Overlay, on_delete=models.CASCADE, default=None)
    convert = models.BooleanField(default=False)
    max_colors = models.IntegerField(default=None, null=True)

    class Meta:
        ordering = ("overlay", "id")
        verbose_name = "  Overlay-Image"
        verbose_name_plural = "  Overlay-Images"

    def image_name(self):
        return f"{self.image.name.split('/')[-1]}"
    image_name.short_description = 'Image'

    def __str__(self):
        return f"{self.image_name()} ({self.id})"

    def save(self, *args, **kwargs):
        img = PIL.Image.open(self.image)
        img = img.convert("RGBA")

        original_width, original_height = img.size
        scale_factor = min(self.width / original_width, self.height / original_height)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        self.width = new_width
        self.height = new_height

        image = img.resize((new_width, new_height), PIL.Image.NEAREST)

        if self.max_colors is not None:
            image = self.__limit_colors(image)

        name = "".join(os.path.basename(self.image.name).split(".")[0:-1])
        png_name = f'{name}.png'
        png_path = settings.FILE_DESTINATION + "layouts/scaled/" + png_name
        image.save(png_path)

        im_matrix = numpy.array(image)

        image_lay = PIL.Image.new('RGBA', (new_width * 3, new_height * 3), (255, 255, 255, 0))
        data = numpy.array(image_lay)

        if self.convert:
            self.__convert_colors(im_matrix, image, new_height, new_width)

        self.__fill_image(data, im_matrix, new_height, new_width)

        fin_image = PIL.Image.fromarray(data)
        img.close()

        name = "".join(os.path.basename(self.image.name).split(".")[0:-1])

        png_name = f'{name}.png'
        png_path = settings.FILE_DESTINATION + "layouts/pixels/" + png_name
        fin_image.save(png_path, quality=100)

        self.layout = png_path

        super().save(*args, **kwargs)

    def __fill_image(self, data, im_matrix, new_height, new_width):
        for i in range(0, new_width):
            for j in range(0, new_height):
                data[j * 3 + 1][i * 3 + 1] = im_matrix[j][i]

                if im_matrix[j][i][3] != 0:
                    data[j * 3 + 1][i * 3 + 1][3] = 255

    def __convert_colors(self, im_matrix, image, new_height, new_width):
        color_array = numpy.array([hex_to_rgb(hex_code) for hex_code in hex_color_palette])
        for y in range(new_height):
            for x in range(new_width):
                pixel = image.getpixel((x, y))

                if pixel[3] != 0:
                    nearest_color = find_nearest_color(color_array, pixel)
                    im_matrix[y][x] = [nearest_color[0], nearest_color[1], nearest_color[2], 255]

    def __limit_colors(self, image):
        image_np = numpy.array(image)
        reshaped_image = numpy.reshape(image_np, (-1, image_np.shape[2]))
        model = KMeans(n_clusters=self.max_colors)
        labels = model.fit_predict(reshaped_image)
        palette = model.cluster_centers_
        quantized_raster = numpy.reshape(palette[labels], image_np.shape).astype(int)
        image = PILImage.fromarray(quantized_raster.astype('uint8'))
        return image


class Tile(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, )
    x = models.IntegerField()
    y = models.IntegerField()
    last_updated = models.DateTimeField()

    class Meta:
        unique_together = ('x', 'y')
        ordering = ('x', 'y')
        verbose_name = "  Tile"
        verbose_name_plural = "  Tiles"
