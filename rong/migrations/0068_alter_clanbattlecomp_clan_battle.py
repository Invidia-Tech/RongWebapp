# Generated by Django 3.2.3 on 2022-03-26 19:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0067_clanbattlescore_comp_locked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='clan_battle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comps', to='rong.clanbattle'),
        ),
    ]
