import json
import time

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from django_redis import get_redis_connection

from quiz.models import Player, Session


class QuizConsumer(AsyncWebsocketConsumer):
    session_id = None
    db_session = None
    player_id = None
    db_player = None
    db_player_gif = None
    is_host = False
    group_name = "quiz_"

    @property
    def cache_key(self):
        return f"quiz:session:{self.session_id}"

    def get_quiz_session(self):
        return Session.objects.filter(pk=self.session_id, is_active=False).first()

    def get_player(self):
        player = Player.objects.filter(pk=self.player_id, session=self.session_id).first()

        if player:
            self.db_player_gif = player.get_gif_url()

        return player

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.player_id = self.scope["url_route"]["kwargs"]["player_id"]

        self.db_session = await database_sync_to_async(self.get_quiz_session)()
        if not self.db_session:
            await self.close()
            return

        self.db_player = await database_sync_to_async(self.get_player)()
        if not self.db_player:
            await self.close()
            return

        self.group_name = f"quiz_{self.session_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.init_redis_session()
        await self.add_player()

    async def disconnect(self, close_code):
        await self.remove_player()
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def init_redis_session(self):
        redis = get_redis_connection("default")
        with redis.lock(f"lock:{self.cache_key}", timeout=2):
            state = cache.get(self.cache_key)
            if not state:
                state = {
                    "phase": "LOBBY",
                    "phase_started_at": None,
                    "phase_ends_at": None,
                    "max_players": self.db_session.max_players,
                    "players": {},
                }
                cache.set(self.cache_key, state, timeout=900)

    async def add_player(self):
        redis = get_redis_connection("default")
        with redis.lock(f"lock:{self.cache_key}", timeout=2):
            state = cache.get(self.cache_key)
            state["players"][self.player_id] = {
                "name": self.db_player.name,
                "gif": self.db_player_gif,
                "is_host": self.db_player.is_host,
                "score": 0,
                "selected_answer": None,
            }
            cache.set(self.cache_key, state, timeout=900)

        await self.broadcast_players()

    async def remove_player(self):
        # Skip if never added
        if not cache.get(self.cache_key) or self.player_id not in cache.get(self.cache_key).get("players", {}):
             return

        redis = get_redis_connection("default")
        with redis.lock(f"lock:{self.cache_key}", timeout=2):
            state = cache.get(self.cache_key)
            if not state:
                return

            # If session not active, remove player
            if not self.db_session.is_active:
                state["players"].pop(self.player_id, None)
            else:
                # If session active, mark player as disconnected
                player = state["players"].get(self.player_id)
                if player:
                    player["disconnected"] = True

            cache.set(self.cache_key, state, timeout=900)

        await self.broadcast_players()

    async def broadcast_players(self):
        state = cache.get(self.cache_key, {"players": {}})
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "player_update",
                "players": list(state["players"].values()),
            },
        )

    async def broadcast_state(self):
        state = cache.get(self.cache_key, {})

        await self.channel_layer.group_send(
            self.group_name,
            {
            "type": "state_update",
            "state": {
                        "phase": state.get("phase"),
                        "phase_started_at": state.get("phase_started_at"),
                        "phase_ends_at": state.get("phase_ends_at"),
                        "players": list(state.get("players", {}).values()),
                    },
            },
        )

    async def player_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "player_update",
            "players": event["players"],
        }))

    async def state_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "state_update",
            "state": event["state"],
        }))

    async def receive(self, text_data):
        """
        Hier kann man Commands vom Client empfangen, z.B.
        - 'start_game' nur vom Host
        - 'answer' von Spielern
        """
        data = json.loads(text_data)
        command = data.get("command")

        if command == "start_game" and self.is_host:
            await self.start_game()
        elif command == "answer":
            await self.submit_answer(data.get("answer"))

    async def start_game(self):
        redis = get_redis_connection("default")
        with redis.lock(f"lock:{self.cache_key}", timeout=2):
            state = cache.get(self.cache_key)
            state["phase"] = "QUESTION"
            now = int(time.time())
            state["phase_started_at"] = now
            state["phase_ends_at"] = now + state.get("time_per_question", 30)
            cache.set(self.cache_key, state, timeout=900)
        await self.broadcast_state()

    async def submit_answer(self, answer):
        """Speichert die Antwort eines Spielers (optional erweitern)"""
        redis = get_redis_connection("default")
        with redis.lock(f"lock:{self.cache_key}", timeout=2):
            state = cache.get(self.cache_key)
            player = state["players"].get(self.channel_name)
            if not player:
                return
            player["answered"] = True
            player["last_answer"] = answer
            cache.set(self.cache_key, state, timeout=900)

        await self.broadcast_state()
