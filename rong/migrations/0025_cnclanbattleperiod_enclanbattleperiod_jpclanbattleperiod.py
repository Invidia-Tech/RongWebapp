# Generated by Django 3.2 on 2021-06-01 07:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0024_clanbattle_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='CNClanBattlePeriod',
            fields=[
                ('id', models.IntegerField(db_column='clan_battle_id', primary_key=True, serialize=False)),
                ('start_time', models.TextField()),
                ('end_time', models.TextField()),
            ],
            options={
                'db_table': 'redive_cn"."clan_battle_period',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ENClanBattlePeriod',
            fields=[
                ('id', models.IntegerField(db_column='clan_battle_id', primary_key=True, serialize=False)),
                ('start_time', models.TextField()),
                ('end_time', models.TextField()),
            ],
            options={
                'db_table': 'redive_en"."clan_battle_period',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='JPClanBattlePeriod',
            fields=[
                ('id', models.IntegerField(db_column='clan_battle_id', primary_key=True, serialize=False)),
                ('start_time', models.TextField()),
                ('end_time', models.TextField()),
            ],
            options={
                'db_table': 'redive_jp"."clan_battle_period',
                'managed': False,
            },
        ),
    ]
