# Generated by Django 3.2 on 2021-05-28 02:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0015_clanbattlescore_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='clanbattlescore',
            name='actual_damage',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='day',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ClanBattleBossInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.PositiveIntegerField()),
                ('lap_from', models.PositiveIntegerField()),
                ('lap_to', models.PositiveIntegerField(null=True)),
                ('boss1_name', models.CharField(max_length=50)),
                ('boss1_hp', models.PositiveIntegerField()),
                ('boss1_pdef', models.PositiveIntegerField()),
                ('boss1_mdef', models.PositiveIntegerField()),
                ('boss1_iconid', models.PositiveIntegerField(null=True)),
                ('boss2_name', models.CharField(max_length=50)),
                ('boss2_hp', models.PositiveIntegerField()),
                ('boss2_pdef', models.PositiveIntegerField()),
                ('boss2_mdef', models.PositiveIntegerField()),
                ('boss2_iconid', models.PositiveIntegerField(null=True)),
                ('boss3_name', models.CharField(max_length=50)),
                ('boss3_hp', models.PositiveIntegerField()),
                ('boss3_pdef', models.PositiveIntegerField()),
                ('boss3_mdef', models.PositiveIntegerField()),
                ('boss3_iconid', models.PositiveIntegerField(null=True)),
                ('boss4_name', models.CharField(max_length=50)),
                ('boss4_hp', models.PositiveIntegerField()),
                ('boss4_pdef', models.PositiveIntegerField()),
                ('boss4_mdef', models.PositiveIntegerField()),
                ('boss4_iconid', models.PositiveIntegerField(null=True)),
                ('boss5_name', models.CharField(max_length=50)),
                ('boss5_hp', models.PositiveIntegerField()),
                ('boss5_pdef', models.PositiveIntegerField()),
                ('boss5_mdef', models.PositiveIntegerField()),
                ('boss5_iconid', models.PositiveIntegerField(null=True)),
                ('clan_battle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bosses', to='rong.clanbattle')),
            ],
        ),
    ]
