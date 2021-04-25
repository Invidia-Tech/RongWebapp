# Generated by Django 3.2 on 2021-04-25 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0003_rename_game_id_clanbattle_game_battle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clan',
            name='role_id',
            field=models.CharField(db_index=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='clancollection',
            name='guild_id',
            field=models.CharField(db_index=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='member',
            name='platform_id',
            field=models.CharField(db_index=True, max_length=30),
        ),
    ]
