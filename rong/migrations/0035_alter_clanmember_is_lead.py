# Generated by Django 3.2.3 on 2021-06-07 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0034_discordmember'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clanmember',
            name='is_lead',
            field=models.BooleanField(default=False),
        ),
    ]
