# Generated by Django 4.2.3 on 2023-07-20 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_image_image_alter_image_preview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='D:\\Benutzer\\Documents\\GitHub\\timeofjustice.eu\\timeofjustice\\data/images/'),
        ),
        migrations.AlterField(
            model_name='image',
            name='preview',
            field=models.ImageField(upload_to='D:\\Benutzer\\Documents\\GitHub\\timeofjustice.eu\\timeofjustice\\data/images/'),
        ),
    ]
