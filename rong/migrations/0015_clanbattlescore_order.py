# Generated by Django 3.2 on 2021-05-28 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0014_auto_20210515_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='clanbattlescore',
            name='order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
