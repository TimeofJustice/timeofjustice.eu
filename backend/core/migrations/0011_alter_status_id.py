# Generated by Django 5.1.2 on 2024-10-30 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_project_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
