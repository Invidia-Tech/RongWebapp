# Generated by Django 3.2 on 2021-05-28 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0020_auto_20210528_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss1_level',
            field=models.PositiveIntegerField(default=60),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss1_multiplier',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss2_level',
            field=models.PositiveIntegerField(default=65),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss2_multiplier',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss3_level',
            field=models.PositiveIntegerField(default=70),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss3_multiplier',
            field=models.DecimalField(decimal_places=2, default=1.1, max_digits=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss4_level',
            field=models.PositiveIntegerField(default=75),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss4_multiplier',
            field=models.DecimalField(decimal_places=2, default=1.1, max_digits=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss5_level',
            field=models.PositiveIntegerField(default=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlebossinfo',
            name='boss5_multiplier',
            field=models.DecimalField(decimal_places=2, default=1.2, max_digits=3),
            preserve_default=False,
        ),
    ]