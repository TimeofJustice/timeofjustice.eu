# Generated by Django 4.2.3 on 2023-07-20 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_alter_image_image_alter_image_preview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='C:/xampp/htdocs/static/data/images/'),
        ),
        migrations.AlterField(
            model_name='image',
            name='preview',
            field=models.ImageField(upload_to='C:/xampp/htdocs/static/data/images/'),
        ),
    ]
