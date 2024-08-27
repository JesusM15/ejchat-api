from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.pagination import PageNumberPagination
from core.models import Post, Like, Comment, CommentImage
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

class PostPagination(PageNumberPagination):
    page_size = 10

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = PostPagination
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        # Combinar request.data y request.FILES
        data = request.data.copy()
        data.setlist('images', request.FILES.getlist('images'))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(user=user, post=post)
        print('Like dado con exito')
        print(created)
        if not created:
            return Response({'detail': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Liked'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(user=user, post=post)
            like.delete()
            return Response({'detail': 'Unliked'}, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({'detail': 'Not liked'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def addComment(self, request, pk=None):
        post = self.get_object()
        data = request.data.copy()
        data['post'] = post.id
        data['user'] = request.user.id
        image = request.FILES.get('images[]')
        if image:
            data['uploaded_image'] = image
        
        serializer = CommentSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        # Obtener la URL de la imagen si existe
        comment_data = serializer.data
        if comment.image:
            comment_data['image_url'] = comment.image.image.url

        # Enviar el mensaje a través de WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'comments_{post.id}',  # Grupo de comentarios para el post
            {
                'type': 'comment_message',
                'comment': comment_data
            }
        )
        print("mensaje enviado")

        return Response(comment_data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def user_posts(self, request):
        print(request)
        user_id = request.query_params.get('user_id')  # Obtener el user_id de los parámetros de consulta
        if user_id is None:
            return Response({'detail': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            posts = Post.objects.filter(user_id=user_id).order_by('-created_at')
            serializer = PostSerializer(posts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'detail': 'Posts not found'}, status=status.HTTP_404_NOT_FOUND)