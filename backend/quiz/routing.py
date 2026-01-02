from django.urls import re_path

from quiz import consumers

websocket_urlpatterns = [
    re_path(r"ws/quiz/(?P<session_id>\w+)$", consumers.QuizConsumer.as_asgi()),
]
