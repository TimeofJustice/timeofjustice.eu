# Generated by Django 5.1.2 on 2025-03-20 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(blank=True, max_length=1000, null=True, upload_to='files/images/profile/'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_short_description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
