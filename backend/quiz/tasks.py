import time

from asgiref.sync import async_to_sync
from background_task import background
from channels.layers import get_channel_layer
from django.core.cache import cache


@background(schedule=10, remove_existing_tasks=True)
def tick_all_sessions():
    channel_layer = get_channel_layer()
    now = int(time.time())

    # alle Redis Keys für aktive Sessions
    client = cache.client.get_client()
    keys = client.keys(":1:quiz:session:*")

    for key in keys:
      # key ist Bytes, decode zuerst
      key_str = key.decode()

      state = cache.get(key_str.split(":1:",1)[-1])

      if not state or not state.get("phase_ends_at"):
          continue

      if now >= state["phase_ends_at"]:
          # Phase wechseln
          if state["phase"] == "QUESTION":
              state["phase"] = "ANSWER"
              state["phase_started_at"] = now
              state["phase_ends_at"] = now + 5
          elif state["phase"] == "ANSWER":
              state["phase"] = "RESULT"
              state["phase_started_at"] = now
              state["phase_ends_at"] = now + 5
              state["question_index"] += 1
          elif state["phase"] == "RESULT":
              state["phase"] = "QUESTION"
              state["phase_started_at"] = now
              state["phase_ends_at"] = now + state["time_per_question"]

          # Redis speichern
          cache.set(key.decode(), state, timeout=900)

          # Broadcast an alle Spieler
          group_name = f"quiz_{key.decode().split(':')[-1]}"
          async_to_sync(channel_layer.group_send)(
              group_name,
              {"type": "state_update", "state": state},
          )
