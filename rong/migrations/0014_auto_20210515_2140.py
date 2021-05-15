# Generated by Django 3.2 on 2021-05-15 09:40

from django.db import migrations, models
import django.db.models.deletion
import rong.models.box_unit

def fill_boxunit_fields(apps, schema_editor):
    BoxUnit = apps.get_model("rong", "BoxUnit")
    for unit in BoxUnit.objects.all():
        if unit.rank is None:
            unit.rank = 1
        if unit.star is None:
            unit.star = unit.unit.rarity
        if unit.level is None:
            unit.level = 1
        if unit.bond is None:
            unit.bond = 1
        unit.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0013_auto_20210507_2020'),
    ]

    operations = [
        migrations.RunPython(fill_boxunit_fields),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.IntegerField(db_column='equipment_id', primary_key=True, serialize=False)),
                ('name', models.TextField(db_column='equipment_name')),
                ('promotion_level', models.IntegerField()),
            ],
            options={
                'db_table': 'redive_en"."equipment_data',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SkillCost',
            fields=[
                ('target_level', models.IntegerField(primary_key=True, serialize=False)),
                ('cost', models.IntegerField()),
            ],
            options={
                'db_table': 'redive_en"."skill_cost',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UnitPromotion',
            fields=[
                ('unit_id', models.IntegerField(primary_key=True, serialize=False)),
                ('promotion_level', models.IntegerField()),
                ('equip1', models.IntegerField(db_column='equip_slot_1')),
                ('equip2', models.IntegerField(db_column='equip_slot_2')),
                ('equip3', models.IntegerField(db_column='equip_slot_3')),
                ('equip4', models.IntegerField(db_column='equip_slot_4')),
                ('equip5', models.IntegerField(db_column='equip_slot_5')),
                ('equip6', models.IntegerField(db_column='equip_slot_6')),
            ],
            options={
                'db_table': 'redive_en"."unit_promotion',
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='boxunit',
            name='bond',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='boxunit',
            name='level',
            field=models.PositiveIntegerField(default=1, validators=[rong.models.box_unit.valid_level]),
        ),
        migrations.AlterField(
            model_name='boxunit',
            name='power',
            field=models.PositiveIntegerField(null=True, validators=[rong.models.box_unit.valid_power]),
        ),
        migrations.AlterField(
            model_name='boxunit',
            name='rank',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='boxunit',
            name='star',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='boxunit',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rong.unit', validators=[rong.models.box_unit.valid_box_unit]),
        ),
    ]
