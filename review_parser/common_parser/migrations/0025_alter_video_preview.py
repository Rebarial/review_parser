# Generated by Django 5.2.2 on 2025-06-26 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_parser', '0024_alter_video_preview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='preview',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
