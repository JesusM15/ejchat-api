# Generated by Django 4.2.13 on 2024-06-30 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='images/default/profile_picture.jpg', null=True, upload_to='profile_pictures/%Y/%m/%d'),
        ),
    ]
