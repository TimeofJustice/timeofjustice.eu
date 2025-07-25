# Generated by Django 5.1.2 on 2025-04-10 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0008_alter_wallet_last_visit_alter_wallet_wallet_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='days_played',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='balance',
            field=models.IntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='wallet_id',
            field=models.CharField(default='7ec34b30ffab4d79b9560a9a8eafc3ed', editable=False, max_length=32, primary_key=True, serialize=False),
        ),
    ]
