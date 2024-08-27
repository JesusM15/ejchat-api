from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatMessageImage

admin.site.register(ChatMessage)
admin.site.register(ChatMessageImage)
admin.site.register(ChatRoom)