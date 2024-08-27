from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from .serializers import UserSerializer, FollowSerializer, FriendshipSerializer, CustomTokenObtainPairSerializer, ProfileSerializer
from .models import Profile, Follow, Friendship
from . import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class ObtainUserFromTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        profile_picture = profile.profile_picture.url if profile.profile_picture else '/media/images/default/profile_picture.jpg'

        # Contar seguidores y seguidos
        following_count = Follow.objects.filter(follower=user).count()
        followers_count = Follow.objects.filter(followed=user).count()


        return Response({
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'last_login': user.last_login,
            'id': user.id,
            "profile": {
                "profile_picture": profile_picture,
                "user_id": profile.user.id,
                "likes_visible": profile.likes_visible,
                "bio": profile.bio,
                'following_count': following_count,
                'followers_count': followers_count
            }
            # Otros campos del usuario que desees devolver
        }, status=status.HTTP_200_OK)
        

class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    
    @action(detail=False, methods=['get'])
    def user_data(self, request):
        print(request)
        user_id = request.query_params.get('user_id')  # Obtener el user_id de los parámetros de consulta
        if user_id is None:
            return Response({'detail': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            profile = get_object_or_404(Profile, user=user)
            profile_picture = profile.profile_picture.url if profile.profile_picture else '/media/images/default/profile_picture.jpg'

    
            # Contar seguidores y seguidos
            following_count = Follow.objects.filter(follower=user).count()
            followers_count = Follow.objects.filter(followed=user).count()

            # Obtener las listas de seguidores y seguidos
            following_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)
            followers_users = Follow.objects.filter(followed=user).values_list('follower', flat=True)

            following_users_data = User.objects.filter(id__in=following_users)
            followers_users_data = User.objects.filter(id__in=followers_users)

            following_users_serializer = UserSerializer(following_users_data, many=True)
            followers_users_serializer = UserSerializer(followers_users_data, many=True)


            return Response({
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'last_login': user.last_login,
                'id': user.id,
                "profile": {
                    "profile_picture": profile_picture,
                    "user_id": profile.user.id,
                    "likes_visible": profile.likes_visible,
                    "bio": profile.bio,
                    'following_count': following_count,
                    'followers_count': followers_count,
                    'following': following_users_serializer.data,
                    'followers': followers_users_serializer.data
                }
                # Otros campos del usuario que desees devolver
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        profile = get_object_or_404(Profile, user=user)

        # Actualización de datos del usuario
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Actualización de datos del perfil
        profile_serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Contar seguidores y seguidos
        following_count = Follow.objects.filter(follower=user).count()
        followers_count = Follow.objects.filter(followed=user).count()
        profile_picture = profile.profile_picture.url if profile.profile_picture else '/media/images/default/profile_picture.jpg'

        # Devolver la información actualizada
        return Response({
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'last_login': user.last_login,
            'id': user.id,
            'profile': {
                'profile_picture': profile_picture,
                'user_id': profile.user.id,
                'likes_visible': profile.likes_visible,
                'bio': profile.bio,
                'following_count': following_count,
                'followers_count': followers_count,
            }
        }, status=status.HTTP_200_OK)
class FollowCreateView(generics.CreateAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("POST request received")
        
        # Obtener el usuario que está haciendo la solicitud
        following_user = request.user
        
        # Obtener el ID del usuario que se quiere seguir desde los datos de la solicitud
        followed_user_id = request.data.get('followed')
        followed_user = get_object_or_404(User, id=followed_user_id)
        
        # Validar que el usuario no se siga a sí mismo
        if following_user == followed_user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el usuario no esté siguiendo ya al usuario destino
        if Follow.objects.filter(follower=following_user, followed=followed_user).exists():
            return Response(
                {"detail": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Guardar el nuevo seguimiento
        Follow.objects.create(follower=following_user, followed=followed_user)
        
        # Verificar si el usuario seguido ya está siguiendo al usuario actual
        if Follow.objects.filter(follower=followed_user, followed=following_user).exists():
            # Crear una relación de amistad
            Friendship.objects.get_or_create(
                user1=following_user,
                user2=followed_user,
                defaults={'status': 'accepted'}
            )
            Friendship.objects.get_or_create(
                user1=followed_user,
                user2=following_user,
                defaults={'status': 'accepted'}
            )
        
        return Response(
            {"detail": "Followed successfully."},
            status=status.HTTP_201_CREATED
        )

class FollowDeleteView(generics.DestroyAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        follower = self.request.user
        followed_user_id = self.kwargs['pk']
        followed_user = get_object_or_404(User, id=followed_user_id)
        return Follow.objects.get(follower=follower, followed=followed_user)

    def perform_destroy(self, instance):
        following_user = instance.follower
        followed_user = instance.followed
        
        # Remove the follow relationship
        instance.delete()
        
        # Remove the friendship relationship if it exists
        Friendship.objects.filter(
            user1=following_user, user2=followed_user
        ).delete()
        Friendship.objects.filter(
            user1=followed_user, user2=following_user
        ).delete()

class FriendshipListView(generics.ListAPIView):
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    
    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(friends__in=[user])

class UserSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class UserSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')

        if query:
            # Buscamos usuarios cuyo username contenga el término de búsqueda
            users = User.objects.filter(Q(username__icontains=query))
            
            if users.exists():
                # Obtener perfiles y contar seguidores
                user_profiles = []
                for user in users:
                    profile = get_object_or_404(Profile, user=user)
                    profile_picture = request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else request.build_absolute_uri('/media/images/default/profile_picture.jpg')

                    # Contar seguidores y seguidos
                    following_count = Follow.objects.filter(follower=user).count()
                    followers_count = Follow.objects.filter(followed=user).count()

                    user_profiles.append({
                        'username': user.username,
                        'is_active': user.is_active,
                        'date_joined': user.date_joined,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'last_login': user.last_login,
                        'id': user.id,
                        "profile": {
                            "profile_picture": profile_picture,
                            "user_id": profile.user.id,
                            "likes_visible": profile.likes_visible,
                            "bio": profile.bio,
                            'following_count': following_count,
                            'followers_count': followers_count
                        }
                    })
                
                # Ordenar los perfiles por número de seguidores en orden descendente
                user_profiles_sorted = sorted(user_profiles, key=lambda x: x['profile']['followers_count'], reverse=True)
                
                return Response(user_profiles_sorted, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "No users found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "No search query provided"}, status=status.HTTP_400_BAD_REQUEST)