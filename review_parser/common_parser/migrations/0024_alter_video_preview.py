# Generated by Django 5.2.2 on 2025-06-25 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_parser', '0023_video_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='preview',
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
    ]
