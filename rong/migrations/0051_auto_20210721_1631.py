# Generated by Django 3.2.3 on 2021-07-21 04:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0050_auto_20210720_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comps',
                                    to='rong.hitgroup'),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hits',
                                    to='rong.hitgroup'),
        ),
        migrations.AlterField(
            model_name='hitgroup',
            name='clan_battle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hit_groups',
                                    to='rong.clanbattle'),
        ),
        migrations.AlterField(
            model_name='hitgroup',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
