# Generated by Django 3.2 on 2021-05-01 09:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0004_auto_20210501_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='clanbattlecomp',
            name='borrowed_unit',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
