# chat/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/general/<int:user_id>/', consumers.GeneralChatConsumer.as_asgi()),
    path('ws/chat/<int:chat_id>/', consumers.ChatConsumer.as_asgi()),
]