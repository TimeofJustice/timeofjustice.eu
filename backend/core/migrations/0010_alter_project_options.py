# Generated by Django 5.1.2 on 2024-10-30 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_status_project_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['status']},
        ),
    ]
