# Generated by Django 5.1.2 on 2024-11-24 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farming_stats', '0008_alter_crop_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name_eng', models.CharField(default='Crop', max_length=50)),
                ('name_de', models.CharField(default='Crop', max_length=50)),
                ('price_jan', models.FloatField(default=0)),
                ('price_feb', models.FloatField(default=0)),
                ('price_mar', models.FloatField(default=0)),
                ('price_apr', models.FloatField(default=0)),
                ('price_may', models.FloatField(default=0)),
                ('price_jun', models.FloatField(default=0)),
                ('price_jul', models.FloatField(default=0)),
                ('price_aug', models.FloatField(default=0)),
                ('price_sep', models.FloatField(default=0)),
                ('price_oct', models.FloatField(default=0)),
                ('price_nov', models.FloatField(default=0)),
                ('price_dec', models.FloatField(default=0)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]