from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Follow, Friendship
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        print(attrs)
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        print("primer user:", user)
        print("email:", email)
        print("password:", password)
        if user is None:
            raise serializers.ValidationError('Contraseña o email invalidos.')
        
        print(user)
        
        return {
            'refresh': str(self.get_token(user)),
            'access': str(self.get_token(user).access_token),
        }

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return refresh

        
# USUARIOS
class ProfileSerializer(serializers.ModelSerializer):
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'bio', 'profile_picture', 'likes_visible', 'followers_count', 'following_count')
        
    def get_following_count(self, obj):
        return obj.following_count()

    def get_followers_count(self, obj):
        return obj.followers_count()
        
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)  # Perfil es de solo lectura

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'profile', 'last_name', 'first_name')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)  # Crear perfil vacío asociado al usuario
        return user

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer()
    followed = UserSerializer()

    class Meta:
        model = Follow
        fields = ('follower', 'followed', 'created_at')

class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ('user1', 'user2', 'status')
        
        
