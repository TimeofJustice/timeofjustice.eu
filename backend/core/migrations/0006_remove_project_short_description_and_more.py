# Generated by Django 5.1.2 on 2024-10-29 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_image_id_alter_project_id_alter_technology_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='short_description',
        ),
        migrations.RemoveField(
            model_name='project',
            name='description',
        ),
        migrations.RemoveField(
            model_name='image',
            name='alt',
        ),
        migrations.AddField(
            model_name='image',
            name='alt_english',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='alt_german',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='alt_yoda',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='alt_english',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='alt_german',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='alt_yoda',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='description_english',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='description_german',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='description_yoda',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='short_description_english',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='short_description_german',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='short_description_yoda',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Text',
        ),
    ]
