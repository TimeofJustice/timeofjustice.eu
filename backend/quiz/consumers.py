import json
import time
import uuid
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from django_redis import get_redis_connection

from quiz.models import Session


class QuizConsumer(AsyncWebsocketConsumer):
    session_id = None
    player_name = None
    is_host = False
    group_name = "quiz_"

    @property
    def cache_key(self):
        return f"quiz:session:{self.session_id}"

    def get_quiz_session(self):
        return Session.objects.filter(pk=self.session_id, is_active=False).first()

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]

        db_session = await database_sync_to_async(self.get_quiz_session)()
        if not db_session:
            await self.close()
            return

        query_params = parse_qs(self.scope["query_string"].decode())
        host_id = query_params.get("host_id", [None])[0]
        self.is_host = host_id == db_session.host_id

        self.group_name = f"quiz_{self.session_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        self.player_name = f"Player-{str(uuid.uuid4())[:8]}"

        await self.init_redis_session(db_session)
        await self.add_player()

    async def disconnect(self, close_code):
        await self.remove_player()
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def init_redis_session(self, db_session):
        redis = get_redis_connection("default")
        with redis.lock(f"lock:{self.cache_key}", timeout=2):
            state = cache.get(self.cache_key)
            if not state:
                now = int(time.time())
                state = {
                    "players": {},
                    "phase": "LOBBY",
                    "question_index": 0,
                    "phase_started_at": now,
                    "phase_ends_at": None,
                    "time_per_question": db_session.time_per_question,
                    "mode": db_session.mode,
                    "max_players": db_session.max_players,
                    "host_id": db_session.host_id,
                }
                cache.set(self.cache_key, state, timeout=900)

    async def add_player(self):
        redis = get_redis_connection("default")
        with redis.lock(f"lock:{self.cache_key}", timeout=2):
            state = cache.get(self.cache_key)
            state["players"][self.channel_name] = {
                "name": self.player_name,
                "score": 0,
                "answered": False,
                "is_host": self.is_host,
            }
            cache.set(self.cache_key, state, timeout=900)

        await self.broadcast_players()
        await self.broadcast_state()

    async def remove_player(self):
        redis = get_redis_connection("default")
        with redis.lock(f"lock:{self.cache_key}", timeout=2):
            state = cache.get(self.cache_key)
            if not state:
                return
            state["players"].pop(self.channel_name, None)
            cache.set(self.cache_key, state, timeout=900)

        await self.broadcast_players()
        await self.broadcast_state()

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
                "state": state,
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
            state["phase_ends_at"] = now + state["time_per_question"]
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
