# Generated by Django 5.1.2 on 2025-04-07 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_alter_wallet_wallet_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='balance',
            field=models.DecimalField(decimal_places=0, default=100, max_digits=20),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='wallet_id',
            field=models.CharField(default='e1013805efc041eca58ad703416062d3', editable=False, max_length=32, primary_key=True, serialize=False),
        ),
    ]
