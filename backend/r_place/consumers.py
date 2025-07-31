import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

from .models import Canvas, Cell


class RPlaceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "r_place",
            self.channel_name,
        )

        await self.accept()
        await self.update_player_count(1)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "r_place",
            self.channel_name,
        )
        await self.update_player_count(-1)

    async def update_player_count(self, delta):
        count = cache.get("r_place_user_count", 0) + delta
        cache.set("r_place_user_count", count, timeout=None)

        await self.channel_layer.group_send("r_place", {
            "type": "player.update",
            "count": count,
        })

    async def player_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "player_update",
            "count": event["count"],
        }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json["type"]

        if message_type == "cell_update":
            await self.handle_cell_update(text_data_json)

    async def handle_cell_update(self, data):
        cell = {
            "x": data["x"],
            "y": data["y"],
            "color": data["color"],
        }

        active_canvas = await database_sync_to_async(self.get_active_canvas)()
        if not active_canvas:
            return

        if not (0 <= cell["x"] < active_canvas.width and 0 <= cell["y"] < active_canvas.height):
            return

        if not isinstance(cell["color"], str) or len(cell["color"]) != 7 or not cell["color"].startswith("#"):
            return

        await database_sync_to_async(self.save_cell)(cell, active_canvas)

        await self.channel_layer.group_send(
            "r_place",
            {
                "type": "cell_update",
                "cell": cell,
            },
        )

    def get_active_canvas(self):
        return Canvas.objects.filter(active=True).first()

    def save_cell(self, cell, canvas):
        Cell.objects.update_or_create(
            x=cell["x"],
            y=cell["y"],
            canvas=canvas,
            defaults={"color": cell["color"]},
        )

    async def cell_update(self, event):
        cell = event["cell"]

        await self.send(text_data=json.dumps(
            {
                "type": "cell_update",
                "cell": cell,
            },
        ))
