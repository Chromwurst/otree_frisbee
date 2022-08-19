from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/socket-otree-server/$', consumers.FbClientConsumer.as_asgi())
]
