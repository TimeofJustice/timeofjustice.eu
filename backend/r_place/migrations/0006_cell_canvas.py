# Generated by Django 5.1.2 on 2025-06-15 17:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('r_place', '0005_canvas_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='canvas',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='cells', to='r_place.canvas'),
        ),
    ]
