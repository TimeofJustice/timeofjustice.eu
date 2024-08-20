import configparser
import datetime
import os
import threading
import time
import numpy
import schedule
from PIL import Image
from peewee import *

if os.name == 'nt':
    ROOT = "./"
else:
    ROOT = "/var/www/timeofjustice.eu/"

CONFIG_FILE = ROOT + 'config.ini'

CONFIG_PARSER = configparser.ConfigParser()
CONFIG_PARSER.read(CONFIG_FILE)

destination = CONFIG_PARSER["DEFAULT"]["IMAGE_DEST_WORKER"]

db = MySQLDatabase(CONFIG_PARSER["DEFAULT"]["SQL_DB"], host='localhost', user=CONFIG_PARSER["DEFAULT"]["SQL_USER"],
                   password=CONFIG_PARSER["DEFAULT"]["SQL_PASS"])

pending = {
    0: {
        0: False,
        250: False,
        500: False,
        750: False
    },
    250: {
        0: False,
        250: False,
        500: False,
        750: False
    },
    500: {
        0: False,
        250: False,
        500: False,
        750: False
    },
    750: {
        0: False,
        250: False,
        500: False,
        750: False
    }
}


class Api_Cell(Model):
    id = PrimaryKeyField()
    x = IntegerField(default=0)
    y = IntegerField(default=0)
    color = CharField(max_length=100)
    last_modified = DateTimeField()
    placed_by = CharField(max_length=100, null=True)

    class Meta:
        database = db


class Api_Tile(Model):
    id = PrimaryKeyField()
    x = IntegerField(default=0)
    y = IntegerField(default=0)
    last_updated = DateTimeField()

    class Meta:
        database = db


def run_threaded_job(job_func, x, y):
    job_thread = threading.Thread(target=job_func, args=(x, y))
    job_thread.start()


def render_tile(x, y):
    global pending

    if pending[x][y]:
        return

    pending[x][y] = True

    try:
        file_name = destination + f"tiles/{x}_{y}.png"

        if os.path.isfile(file_name):
            image = Image.open(file_name)
            image = image.convert("RGBA")
            image = image.resize((250, 250), Image.LANCZOS)
            data = numpy.array(image)

            tiles = (Api_Tile
                     .select().where((Api_Tile.x == x) &
                                     (Api_Tile.y == y)))

            date = tiles[0].last_updated - datetime.timedelta(seconds=2)

            cells = (Api_Cell
                     .select()
                     .where((Api_Cell.x >= x) &
                            (Api_Cell.x <= x + 249) &
                            (Api_Cell.y >= y) &
                            (Api_Cell.y <= y + 249) &
                            (Api_Cell.last_modified >= date)))

            if len(cells) != 0:
                tiles[0].last_updated = datetime.datetime.now(datetime.timezone.utc)
                tiles[0].save()
        else:
            tiles = (Api_Tile
                     .select().where((Api_Tile.x == x) &
                                     (Api_Tile.y == y)))

            if len(tiles) == 0:
                new_tile = Api_Tile.create(x=x, y=y, last_updated=datetime.datetime.now(datetime.timezone.utc))
                new_tile.save()

            image = Image.new('RGBA', (250, 250), (255, 255, 255, 0))
            data = numpy.array(image)

            cells = (Api_Cell
                     .select()
                     .where((Api_Cell.x >= x) &
                            (Api_Cell.x <= x + 249) &
                            (Api_Cell.y >= y) &
                            (Api_Cell.y <= y + 249)))

        if len(cells) != 0:
            for cell in cells:
                data[cell.y - y][cell.x - x] = [int(cell.color[1:][i:i + 2], 16) for i in (0, 2, 4)] + [255]

            image = Image.fromarray(data)

            image.save(file_name)
    except Exception as e:
        print(f"Error in Thread-{x}-{y}: {e}")

    pending[x][y] = False


interval = 1


schedule.every(interval).seconds.do(run_threaded_job, render_tile, 0, 0)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 250, 0)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 500, 0)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 750, 0)

schedule.every(interval).seconds.do(run_threaded_job, render_tile, 0, 250)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 250, 250)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 500, 250)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 750, 250)

schedule.every(interval).seconds.do(run_threaded_job, render_tile, 0, 500)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 250, 500)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 500, 500)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 750, 500)

schedule.every(interval).seconds.do(run_threaded_job, render_tile, 0, 750)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 250, 750)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 500, 750)
schedule.every(interval).seconds.do(run_threaded_job, render_tile, 750, 750)

while True:
    schedule.run_pending()
    time.sleep(1)
