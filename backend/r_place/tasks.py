import datetime
from pathlib import Path

import numpy as np
from background_task import background
from django.conf import settings
from PIL import Image

from r_place import models


@background(schedule=60 * 5, remove_existing_tasks=True)
def render_canvas():
    canvas = models.Canvas.objects.filter(active=True).first()

    if not canvas:
        return

    current_time = datetime.datetime.now(datetime.UTC)

    image_name = f'{canvas.name}-{current_time.strftime("%Y%m%d-%H%M%S")}.png'

    canvas_image = f"{settings.FILE_DESTINATION}images/r-place/{image_name}"
    Path(canvas_image).parent.mkdir(parents=True, exist_ok=True)

    cells = models.Cell.objects.filter(
        canvas=canvas,
    ).exclude(color__iexact="#ffffff").values("x", "y", "color")
    cells = list(cells)

    image = Image.new('RGBA', (canvas.width, canvas.height), (255, 255, 255, 255))
    data = np.array(image)

    for cell in cells:
        x = cell['x']
        y = cell['y']
        color = cell['color']

        if color:
            r, g, b = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                data[y, x] = [r, g, b, 255]

    image = Image.fromarray(data, 'RGBA')
    image.save(canvas_image, format='PNG')
    image.close()

    rendered_canvas = models.RenderedCanvas(
        canvas=canvas,
        image_name=image_name,
        created_at=current_time,
    )
    rendered_canvas.save()
