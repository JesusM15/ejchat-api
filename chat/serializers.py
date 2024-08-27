# chat/serializers.py
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatMessageImage
from core.models import Post, Like, Image, Profile, Comment, CommentImage
from django.contrib.auth.models import User


#POST
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'user', 'bio', 'profile_picture', 'likes_visible')
        
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)  # Perfil es de solo lectura
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'profile', 'last_name', 'first_name', 'profile_picture', 'is_active')
        
    def get_profile_picture(self, obj):
        profile = get_object_or_404(Profile, user=obj)
        if profile.profile_picture:
            return profile.profile_picture.url
        return '/media/images/default/profile_picture.jpg'  # URL de la imagen por defecto

class ChatMessageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageImage
        fields = ('id', 'image')

class ChatMessageReadSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)  # Usa el serializer de usuario para lectura
    images = ChatMessageImageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = ('id', 'chat_room', 'sender', 'content', 'timestamp', 'images')

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    images = ChatMessageImageSerializer(many=True, read_only=True)
    # Ya no necesitamos uploaded_images

    class Meta:
        model = ChatMessage
        fields = ('id', 'chat_room', 'sender', 'content', 'timestamp', 'images')

    def create(self, validated_data):
        # Obtener las imágenes subidas desde el request
        request = self.context['request']
        uploaded_images = request.FILES.getlist('images[]')

        # Crear el mensaje de chat
        message = ChatMessage.objects.create(**validated_data)

        # Asociar las imágenes con el mensaje
        for image in uploaded_images:
            ChatMessageImage.objects.create(message=message, image=image)

        return message


class ChatRoomSerializer(serializers.ModelSerializer):
    participant1 = UserSerializer(read_only=True)
    participant2 = UserSerializer(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = '__all__'
