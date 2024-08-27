import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class GeneralChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'general_chat_{self.user_id}'

        # Únete al grupo de chat general del usuario
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo de chat general
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        chat_id = text_data_json.get('chat_id')  # Usa .get() para evitar KeyError

        # Enviar el mensaje a todos los usuarios en el grupo de chat general
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'general_message',
                'message': message,
                'chat_id': chat_id
            }
        )

    async def general_message(self, event):
        message = event['message']
        chat_id = event['chat_id']

        # Enviar el mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'chat_id': chat_id
        }))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        # Únete al grupo de chat específico
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo de chat específico
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # Guardar el mensaje en la base de datos
        message_instance = await database_sync_to_async(ChatMessage.objects.create)(
            chat_id=self.chat_id,
            sender_id=sender_id,
            content=message
        )

        # Serializar el mensaje
        serializer = ChatMessageSerializer(message_instance)
        message_data = serializer.data

        # Enviar el mensaje al grupo de chat específico
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Enviar el mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))