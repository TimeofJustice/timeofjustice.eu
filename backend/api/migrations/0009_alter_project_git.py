# Generated by Django 4.2.3 on 2023-07-19 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_image_preview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='git',
            field=models.URLField(null=True),
        ),
    ]
