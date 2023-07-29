import datetime
import os
import numpy
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore, register_events

from ..models import Cell


def test():
    destination = 'home/jonas/timeofjustice.eu/timeofjustice/data/images/'

    if os.name == 'nt':
        destination = 'C:/xampp/htdocs/timeofjustice.eu/timeofjustice/static/data/images/'

    for y_ in range(0, 4):
        for x_ in range(0, 4):
            x = x_ * 250
            y = y_ * 250

            file_name = destination + f"{x}_{y}.png"

            if os.path.isfile(file_name):
                image = Image.open(file_name)
                image = image.convert("RGBA")
                image = image.resize((250, 250), Image.LANCZOS)
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
                image = Image.new('RGBA', (250, 250), (255, 255, 255, 0))
                data = numpy.array(image)

                cells = Cell.objects.filter(
                    x__gte=x,
                    x__lte=x + 249,
                    y__gte=y,
                    y__lte=y + 249
                )

            if len(cells) != 0:
                for cell in cells:
                    data[cell.y - y][cell.x - x] = [int(cell.color[1:][i:i + 2], 16) for i in (0, 2, 4)] + [255]

                image = Image.fromarray(data)

                image.save(file_name)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(test, "interval", seconds=1, jobstore="default", id="test", replace_existing=True)
    register_events(scheduler)
    scheduler.start()
