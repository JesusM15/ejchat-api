from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    participant1 = models.ForeignKey(User, related_name='chatroom_participant1', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(User, related_name='chatroom_participant2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participant1', 'participant2')  # Asegura que no haya duplicados

    def save(self, *args, **kwargs):
        # Asegurarse de que participant1 siempre tenga el menor ID
        if self.participant1.id > self.participant2.id:
            self.participant1, self.participant2 = self.participant2, self.participant1
        super(ChatRoom, self).save(*args, **kwargs)

    def __str__(self):
        return f'Chat between {self.participant1.username} and {self.participant2.username}'

class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)  # Texto del mensaje
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username}: {self.content[:50]}'  # Mostrar los primeros 50 caracteres del mensaje

class ChatMessageImage(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='chat_images/%Y/%m/%d')

    def __str__(self):
        return f'Image for message {self.message.id}'
