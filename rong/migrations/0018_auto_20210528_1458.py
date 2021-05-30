# Generated by Django 3.2 on 2021-05-28 02:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0017_auto_20210528_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='clanbattlescore',
            name='is_carryover',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='is_last_hit',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='clan_battle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hits', to='rong.clanbattle'),
        ),
    ]