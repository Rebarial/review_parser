# Generated by Django 5.2.2 on 2025-06-11 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common_parser', '0004_branch_twogis_map_link_alter_branch_yandex_map_link'),
    ]

    operations = [
        migrations.RenameField(
            model_name='branch',
            old_name='twogis_map_link',
            new_name='twogis_map_url',
        ),
        migrations.RenameField(
            model_name='branch',
            old_name='yandex_map_link',
            new_name='yandex_map_url',
        ),
        migrations.RenameField(
            model_name='organization',
            old_name='title',
            new_name='name',
        ),
    ]
