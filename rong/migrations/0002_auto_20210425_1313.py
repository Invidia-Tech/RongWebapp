# Generated by Django 3.2 on 2021-04-25 01:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clanbattlecomp',
            old_name='boss_lap',
            new_name='boss_phase',
        ),
        migrations.RemoveField(
            model_name='availableunit',
            name='equip_1',
        ),
        migrations.RemoveField(
            model_name='availableunit',
            name='equip_2',
        ),
        migrations.RemoveField(
            model_name='availableunit',
            name='equip_3',
        ),
        migrations.RemoveField(
            model_name='availableunit',
            name='equip_4',
        ),
        migrations.RemoveField(
            model_name='availableunit',
            name='equip_5',
        ),
        migrations.AddField(
            model_name='clanbattlecomp',
            name='borrowed_unit_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlecomp',
            name='unit1_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlecomp',
            name='unit2_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlecomp',
            name='unit3_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlecomp',
            name='unit4_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='unit1scores', to='rong.unit'),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit1_damage',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit1_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='unit2scores', to='rong.unit'),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit2_damage',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit2_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit3',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='unit3scores', to='rong.unit'),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit3_damage',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit3_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit4',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='unit4scores', to='rong.unit'),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit4_damage',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit4_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit5',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='unit5scores', to='rong.unit'),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit5_damage',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='unit5_star',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='availableunit',
            name='rank',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='borrowed_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='borrowedcomps', to='rong.unit'),
        ),
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='unit1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='unit1comps', to='rong.unit'),
        ),
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='unit2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='unit2comps', to='rong.unit'),
        ),
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='unit3',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='unit3comps', to='rong.unit'),
        ),
        migrations.AlterField(
            model_name='clanbattlecomp',
            name='unit4',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='unit4comps', to='rong.unit'),
        ),
    ]
