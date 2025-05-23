# Generated by Django 4.2.13 on 2024-08-24 23:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatroom_chatmessage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmessage',
            name='attachment',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='image',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='video',
        ),
        migrations.CreateModel(
            name='ChatMessageImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='chat_images/%Y/%m/%d')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='chat.chatmessage')),
            ],
        ),
    ]
