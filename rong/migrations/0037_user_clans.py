# Generated by Django 3.2.3 on 2021-06-07 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0036_auto_20210607_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='clans',
            field=models.ManyToManyField(through='rong.ClanMember', to='rong.Clan'),
        ),
    ]
