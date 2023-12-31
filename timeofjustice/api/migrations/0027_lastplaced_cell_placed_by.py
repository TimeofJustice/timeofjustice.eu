# Generated by Django 4.2.3 on 2023-07-25 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_alter_cell_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastPlaced',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='cell',
            name='placed_by',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
