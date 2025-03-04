# Generated by Django 5.1.2 on 2024-10-29 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(default='Description is missing'),
        ),
        migrations.AlterField(
            model_name='project',
            name='github',
            field=models.URLField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='technology',
            field=models.ManyToManyField(null=True, to='core.technology'),
        ),
        migrations.AlterField(
            model_name='project',
            name='webpage',
            field=models.URLField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='technology',
            name='icon',
            field=models.CharField(max_length=25, null=True),
        ),
    ]
