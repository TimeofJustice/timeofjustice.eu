# Generated by Django 5.1.2 on 2024-11-23 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farmingStats', '0004_alter_crop_harvest_month_alter_crop_planting_month'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crop',
            name='name_yoda',
        ),
    ]
