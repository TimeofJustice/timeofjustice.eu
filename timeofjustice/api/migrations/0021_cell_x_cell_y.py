# Generated by Django 4.2.3 on 2023-07-20 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_cell'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='x',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cell',
            name='y',
            field=models.IntegerField(default=0),
        ),
    ]
