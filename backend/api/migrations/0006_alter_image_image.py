# Generated by Django 4.2.3 on 2023-07-19 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_tag_options_alter_project_git'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.FileField(upload_to='D:\\Benutzer\\Documents\\GitHub\\timeofjustice.eu\\timeofjustice\\api/static/images/'),
        ),
    ]
