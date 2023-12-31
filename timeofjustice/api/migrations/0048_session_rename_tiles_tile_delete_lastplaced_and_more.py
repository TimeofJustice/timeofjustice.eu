# Generated by Django 4.2.3 on 2023-07-31 13:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0047_remove_tiles_delta_update'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('last_placed', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid_until', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': '  Session',
                'verbose_name_plural': '  Sessions',
                'ordering': ('-last_placed',),
            },
        ),
        migrations.RenameModel(
            old_name='Tiles',
            new_name='Tile',
        ),
        migrations.DeleteModel(
            name='LastPlaced',
        ),
        migrations.AlterModelOptions(
            name='cell',
            options={'ordering': ('-last_modified', 'x', 'y'), 'verbose_name': '  Cell', 'verbose_name_plural': '  Cells'},
        ),
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ('project', 'index'), 'verbose_name': ' Image', 'verbose_name_plural': ' Images'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('-name',), 'verbose_name': ' Project', 'verbose_name_plural': ' Projects'},
        ),
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ('id',), 'verbose_name': ' Status', 'verbose_name_plural': ' Status'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': ' Tag', 'verbose_name_plural': ' Tags'},
        ),
        migrations.RenameField(
            model_name='project',
            old_name='languages',
            new_name='tags',
        ),
        migrations.AlterField(
            model_name='cell',
            name='color',
            field=models.CharField(max_length=7),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(max_length=255, upload_to='C:/xampp/htdocs/timeofjustice.eu/timeofjustice/static/data/images/projects/'),
        ),
        migrations.AlterField(
            model_name='image',
            name='preview',
            field=models.ImageField(editable=False, max_length=255, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='overlayimage',
            name='image',
            field=models.ImageField(max_length=255, upload_to='C:/xampp/htdocs/timeofjustice.eu/timeofjustice/static/data/images/layouts/originals'),
        ),
        migrations.AlterField(
            model_name='placetimeout',
            name='id',
            field=models.AutoField(auto_created=True, default=0, primary_key=True, serialize=False),
        ),
    ]
