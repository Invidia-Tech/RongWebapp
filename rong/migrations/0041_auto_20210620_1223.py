# Generated by Django 3.2.3 on 2021-06-20 00:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0040_rename_game_id_clanmember_player_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clanbattle',
            name='boss1_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='clanbattle',
            name='boss2_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='clanbattle',
            name='boss3_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='clanbattle',
            name='boss4_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='clanbattle',
            name='boss5_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
