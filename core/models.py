from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/%Y/%m/%d', null=True, blank=True, default="images/default/profile_picture.jpg")  # Cambié %M a %m para el mes
    bio = models.TextField(null=True, blank=True)
    likes_visible = models.BooleanField(default=True)

    def following_count(self):
        return Follow.objects.filter(follower=self.user).count()

    def followers_count(self):
        return Follow.objects.filter(followed=self.user).count()

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'followed')
        
# core/models.py
class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name='friendship_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friendship_user2', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('accepted', 'Accepted')))

    def save(self, *args, **kwargs):
        if self.user1 and self.user2:
            if self.user1.id > self.user2.id:
                self.user1, self.user2 = self.user2, self.user1
        super(Friendship, self).save(*args, **kwargs)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    images = models.ManyToManyField('Image')
    
    def __str__(self):
        return self.content

    @property
    def likes_count(self):
        return self.likes.count()
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Asegura que un usuario no pueda dar like al mismo post más de una vez

    def __str__(self):
        return f'{self.user.username} likes {self.post.id}'

class Image(models.Model):
    image = models.ImageField(upload_to='post_images/%Y/%m/%d')  # Cambié %M a %m para el mes
    
    def get_absolute_url(self):
        request = self.context.get('request')
        if request and self.image:
            return request.build_absolute_uri(self.image.url)
        return None

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.OneToOneField('CommentImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='comment')
    
    def __str__(self):
        return f'"{self.content}" por: {self.user.username} en "{self.post.content}"'

class CommentImage(models.Model):
    image = models.ImageField(upload_to='comment_images/%Y/%m/%d')
    
    def get_absolute_url(self):
        request = self.context.get('request')
        if request and self.image:
            return request.build_absolute_uri(self.image.url)
        return None

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)