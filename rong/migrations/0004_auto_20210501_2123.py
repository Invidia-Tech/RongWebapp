# Generated by Django 3.2 on 2021-05-01 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0003_auto_20210425_1319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='borrowed_unit',
        ),
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='borrowed_unit_star',
        ),
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='unit1',
        ),
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='unit1_star',
        ),
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='unit2',
        ),
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='unit2_star',
        ),
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='unit3',
        ),
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='unit3_star',
        ),
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='unit4',
        ),
        migrations.RemoveField(
            model_name='clanbattlecomp',
            name='unit4_star',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit1',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit1_star',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit2',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit2_star',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit3',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit3_star',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit4',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit4_star',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit5',
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='unit5_star',
        ),
        migrations.AddField(
            model_name='availableunit',
            name='bond',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='availableunit',
            name='equip1',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='availableunit',
            name='equip2',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='availableunit',
            name='equip3',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='availableunit',
            name='equip4',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='availableunit',
            name='equip5',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='availableunit',
            name='equip6',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='availableunit',
            name='level',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='availableunit',
            name='power',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='availableunit',
            name='rank',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='availableunit',
            name='star',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='boss_number',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='boss_phase',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='damage',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='boss_lap',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='boss_number',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='damage',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='unit1_damage',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='unit2_damage',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='unit3_damage',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='unit4_damage',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='clanbattlescore',
            name='unit5_damage',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='group_num',
            field=models.PositiveIntegerField(),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('power', models.PositiveIntegerField(null=True)),
                ('unit1_star', models.PositiveIntegerField(null=True)),
                ('unit1_level', models.PositiveIntegerField(null=True)),
                ('unit2_star', models.PositiveIntegerField(null=True)),
                ('unit2_level', models.PositiveIntegerField(null=True)),
                ('unit3_star', models.PositiveIntegerField(null=True)),
                ('unit3_level', models.PositiveIntegerField(null=True)),
                ('unit4_star', models.PositiveIntegerField(null=True)),
                ('unit4_level', models.PositiveIntegerField(null=True)),
                ('unit5_level', models.PositiveIntegerField(null=True)),
                ('unit5_star', models.PositiveIntegerField(null=True)),
                ('unit1', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='unit1teams',
                                            to='rong.unit')),
                ('unit2', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='unit2teams',
                                            to='rong.unit')),
                ('unit3', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='unit3teams',
                                            to='rong.unit')),
                ('unit4', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='unit4teams',
                                            to='rong.unit')),
                ('unit5', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='unit5teams',
                                            to='rong.unit')),
            ],
        ),
        migrations.CreateModel(
            name='PrincessArenaComp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('user_id', models.PositiveIntegerField(null=True)),
                ('last_updated', models.DateTimeField()),
                ('notes', models.TextField()),
                ('pfp_unit', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='rong.unit')),
                ('team1', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='team1_for',
                                               to='rong.team')),
                ('team2', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='team2_for',
                                               to='rong.team')),
                ('team3',
                 models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team3_for',
                                      to='rong.team')),
            ],
        ),
        migrations.CreateModel(
            name='BattleArenaCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_defense', models.BooleanField()),
                ('last_updated', models.DateTimeField()),
                ('upvotes', models.PositiveIntegerField()),
                ('downvotes', models.PositiveIntegerField()),
                ('notes', models.TextField()),
                ('attacker_team',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='attacker_in',
                                      to='rong.team')),
                ('defender_team',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='defender_in',
                                      to='rong.team')),
                ('submitter',
                 models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rong.member')),
            ],
        ),
        migrations.AddField(
            model_name='clanbattlecomp',
            name='team',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='rong.team'),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='team',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rong.team'),
        ),
    ]
