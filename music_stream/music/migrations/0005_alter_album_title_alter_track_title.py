# Generated by Django 5.2.4 on 2025-07-21 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_alter_trackinalbum_options_alter_album_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='title',
            field=models.CharField(max_length=128, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='track',
            name='title',
            field=models.CharField(max_length=128, verbose_name='Название'),
        ),
    ]
