import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Message, Cell


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        messages = await database_sync_to_async(self.get_messages)()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "initial_messages",
                    "messages": messages
                }
            )
        )

    def get_messages(self):
        messages = Message.objects.filter(room=self.room_name)
        return [msg.message for msg in messages]

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await database_sync_to_async(self.save_message)(message)

        print("Received message:", message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    def save_message(self, message):
        Message.objects.create(room=self.room_name, message=message)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        print("chat_message message:", message)

        # Send message to WebSocket
        await self.send(text_data=json.dumps(
            {
                "type": "new_message",
                "message": message
            }
        ))


class RPlaceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "r_place",
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "r_place",
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json["type"]

        if type == "cell_update":
            await self.handle_cell_update(text_data_json)

    async def handle_cell_update(self, data):
        cell = {
            "x": data["x"],
            "y": data["y"],
            "color": data["color"]
        }

        await database_sync_to_async(self.save_cell)(cell)

        await self.channel_layer.group_send(
            "r_place",
            {
                "type": "cell.update",
                "cell": cell
            }
        )

    def save_cell(self, cell):
        Cell.objects.update_or_create(
            x=cell["x"],
            y=cell["y"],
            defaults={"color": cell["color"]}
        )

    async def cell_update(self, event):
        cell = event["cell"]

        await self.send(text_data=json.dumps(
            {
                "type": "cell_update",
                "cell": cell
            }
        ))
