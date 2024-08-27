# chat/urls.py
from django.urls import path
from .views import ChatRoomListView, ChatMessageCreateView,  CreateOrRetrieveChatView, ChatMessagesListView

urlpatterns = [
    path('chatrooms/', ChatRoomListView.as_view(), name='chatroom_list'),
    # path('chatrooms/<int:chat_room_id>/messages/', ChatRoomListView.as_view(), name='chatmessage_list'),
    path('chatrooms/create-or-retrieve/', CreateOrRetrieveChatView.as_view(), name='create_or_retrieve'),
    path('chatrooms/<int:chat_id>/messages/', ChatMessageCreateView.as_view(), name='chat_message_create'),
    path('<int:chat_id>/messages/', ChatMessagesListView.as_view(), name='chat-messages'),

]
