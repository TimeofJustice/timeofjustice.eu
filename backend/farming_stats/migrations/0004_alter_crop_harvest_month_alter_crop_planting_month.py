# Generated by Django 5.1.2 on 2024-11-23 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farming_stats', '0003_remove_crop_name_crop_name_de_crop_name_eng_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crop',
            name='harvest_month',
            field=models.CharField(choices=[('january', 'january'), ('february', 'february'), ('march', 'march'), ('april', 'april'), ('may', 'may'), ('june', 'june'), ('july', 'july'), ('august', 'august'), ('september', 'september'), ('october', 'october'), ('november', 'november'), ('december', 'december')], default='january', max_length=50),
        ),
        migrations.AlterField(
            model_name='crop',
            name='planting_month',
            field=models.CharField(choices=[('january', 'january'), ('february', 'february'), ('march', 'march'), ('april', 'april'), ('may', 'may'), ('june', 'june'), ('july', 'july'), ('august', 'august'), ('september', 'september'), ('october', 'october'), ('november', 'november'), ('december', 'december')], default='january', max_length=50),
        ),
    ]
