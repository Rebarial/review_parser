# Generated by Django 5.2.2 on 2025-06-11 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_parser', '0009_branch_vlru_review_avg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='vlru_review_avg',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
