# chat/views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer, ChatMessageReadSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets, status

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class CreateOrRetrieveChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        target_user_id = request.data.get('target_user_id')

        if not target_user_id:
            return Response({"error": "Target user id is required"}, status=400)

        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({"error": "Target user does not exist"}, status=404)

        # Verifica si el chat ya existe
        chat = ChatRoom.objects.filter(
            Q(participant1=user, participant2=target_user) |
            Q(participant1=target_user, participant2=user)
        ).first()
        
        if chat:
            # Si el chat ya existe, retornarlo
            return Response(ChatRoomSerializer(chat).data)

        # Si no existe, crear un nuevo chat
        new_chat = ChatRoom.objects.create(participant1=user, participant2=target_user)

        return Response(ChatRoomSerializer(new_chat).data)


class ChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Desactiva la paginación


    def get_queryset(self):
        # Devuelve todos los chats en los que el usuario está involucrado
        chats =  ChatRoom.objects.filter(
            Q(participant1=self.request.user) | Q(participant2=self.request.user)
        )
        print(chats)
        
        return chats

class ChatRoomDetailView(generics.RetrieveAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Devuelve el chat específico si el usuario está involucrado
        return ChatRoom.objects.filter(
            Q(participant1=self.request.user) | Q(participant2=self.request.user)
        )
        
class ChatMessagesListView(generics.ListAPIView):
    serializer_class = ChatMessageReadSerializer
    pagination_class = None  # Desactiva la paginación

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return ChatMessage.objects.filter(chat_room_id=chat_id).order_by('-timestamp')

class ChatMessageCreateView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Combinar request.data y request.FILES
        data = request.data.copy()
        # Asegúrate de que las imágenes están en request.FILES
        images = request.FILES.getlist('images[]')
        
        # Reemplazar el campo 'images' en data con las imágenes en request.FILES
        data.setlist('images[]', images)

        # Pasar el contexto actual del request al serializer
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Obtener la instancia del mensaje creado
        message = serializer.instance

        # Serializar el mensaje creado
        message_data = ChatMessageReadSerializer(message).data

        # Obtener el canal de WebSockets
        channel_layer = get_channel_layer()

        # Enviar el mensaje al grupo de chat específico
        async_to_sync(channel_layer.group_send)(
            f"chat_{message.chat_room.id}",
            {
                "type": "chat_message",
                "message": message_data
            }
        )

        # Enviar el mensaje a los grupos generales de los participantes
        participants = [message.chat_room.participant1, message.chat_room.participant2]
        for participant in participants:
            group_name = f"general_chat_{participant.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "general_message",
                    "message": message_data,
                    "chat_id": message.chat_room.id,
                }
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

