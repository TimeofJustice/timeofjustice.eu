import os
import numpy
from background_task import background
from PIL import Image

from django.conf import settings
from r_place import models


@background(schedule=60 * 5, remove_existing_tasks=True)
def notify_user():
    canvas = models.Canvas.objects.filter(active=True).first()

    if not canvas:
        return

    canvas_image = f'{settings.FILE_DESTINATION}images/r-place/{canvas.name}.png'
    os.makedirs(os.path.dirname(canvas_image), exist_ok=True)

    cells = models.Cell.objects.filter(
        canvas=canvas
    ).exclude(color__iexact="#ffffff").values("x", "y", "color")
    cells = list(cells)

    image = Image.new('RGBA', (canvas.width, canvas.height), (255, 255, 255, 255))
    data = numpy.array(image)

    for cell in cells:
        x = cell['x']
        y = cell['y']
        color = cell['color']

        if color:
            r, g, b = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
            data[y, x] = [r, g, b, 255]

    image = Image.fromarray(data, 'RGBA')
    image.save(canvas_image, format='PNG')
