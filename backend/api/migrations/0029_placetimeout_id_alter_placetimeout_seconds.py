# Generated by Django 4.2.3 on 2023-07-25 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_placetimeout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placetimeout',
            name='id',
            field=models.IntegerField(auto_created=True, default=0, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='placetimeout',
            name='seconds',
            field=models.IntegerField(default=0),
        ),
    ]
