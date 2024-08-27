from django.contrib import admin
from .models import Profile, Post, Image, Comment, Message, Like, CommentImage

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Image)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Message)
admin.site.register(CommentImage)
