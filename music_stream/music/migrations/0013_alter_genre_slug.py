# Generated by Django 5.2.4 on 2025-07-27 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0012_remove_genre_bpm_genre_max_bpm_genre_min_bpm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='slug',
            field=models.SlugField(max_length=128),
        ),
    ]
