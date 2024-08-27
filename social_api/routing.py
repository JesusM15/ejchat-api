# social_api/routing.py
from django.urls import path
from .consumers import CommentConsumer

websocket_urlpatterns = [
    path('ws/comments/<int:post_id>/', CommentConsumer.as_asgi()),
]
