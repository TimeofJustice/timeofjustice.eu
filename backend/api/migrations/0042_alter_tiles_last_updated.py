# Generated by Django 4.2.3 on 2023-07-30 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_alter_tiles_last_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tiles',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
