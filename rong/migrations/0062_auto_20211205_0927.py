# Generated by Django 3.2.3 on 2021-12-04 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0061_clan_platform_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnlockUnitCondition',
            fields=[
                ('id', models.AutoField(db_column='unit_id', primary_key=True, serialize=False)),
                ('condition_id_1', models.IntegerField()),
            ],
            options={
                'db_table': 'redive_en"."unlock_unit_condition',
                'managed': False,
            },
        ),
        migrations.AddField(
            model_name='boxunit',
            name='notes',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='boxunit',
            name='ue_level',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.CreateModel(
            name='BoxItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('box', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to='rong.box')),
            ],
        ),
        migrations.AddConstraint(
            model_name='boxitem',
            constraint=models.UniqueConstraint(fields=('box', 'item'), name='unique box item'),
        ),
    ]
