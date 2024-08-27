from django.shortcuts import get_object_or_404
from rest_framework import serializers
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

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('user', 'post', 'created_at')
        
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', )
        
    def get_image(self, obj):
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
        
class CommentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = ('image',)
        
    def get_image(self, obj):
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = CommentImageSerializer(required=False, read_only=True)
    uploaded_image = serializers.ImageField(write_only=True, required=False)


    class Meta:
        model = Comment
        fields = ('id', 'user', 'content', 'created_at', 'post', 'image', 'uploaded_image')

    def create(self, validated_data):
        print(validated_data)
        uploaded_image = validated_data.pop('uploaded_image', None)
        user = self.context['request'].user
        comment = Comment.objects.create(user=user, **validated_data)

        if uploaded_image:
            image_instance = CommentImage.objects.create(image=uploaded_image)
            comment.image = image_instance
            comment.save()

        return comment
        
class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.ReadOnlyField()
    # gestion imagenes
    images = ImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    
    class Meta:
        model = Post
        fields = ('id', 'user', 'content', 'created_at', 'images', 'likes_count', 'uploaded_images', 'likes', 'comments')
        

    def create(self, validated_data):
        uploaded_images = self.context['request'].FILES.getlist('images[]', [])
        user = self.context['request'].user
        post = Post.objects.create(user=user, **validated_data)

        for image in uploaded_images:
            image_instance = Image.objects.create(image=image)
            post.images.add(image_instance)

        return post