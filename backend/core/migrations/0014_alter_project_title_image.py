# Generated by Django 5.1.2 on 2024-12-02 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_status_options_status_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='title_image',
            field=models.ImageField(blank=True, max_length=1000, null=True, upload_to='files/images/project/'),
        ),
    ]
