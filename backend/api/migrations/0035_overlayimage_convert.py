# Generated by Django 4.2.3 on 2023-07-27 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_alter_cell_last_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='overlayimage',
            name='convert',
            field=models.BooleanField(default=False),
        ),
    ]
