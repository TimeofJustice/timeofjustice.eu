from django.urls import re_path

from r_place import consumers

websocket_urlpatterns = [
    re_path(r"ws/r-place/", consumers.RPlaceConsumer.as_asgi()),
]
