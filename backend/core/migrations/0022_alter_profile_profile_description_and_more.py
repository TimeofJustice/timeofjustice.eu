# Generated by Django 5.1.2 on 2025-03-20 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_alter_profile_profile_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_description',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_short_description',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
