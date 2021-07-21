# Generated by Django 3.2.3 on 2021-07-20 10:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0049_auto_20210720_2053'),
    ]

    operations = [
        migrations.CreateModel(
            name='HitTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('clan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rong.clan')),
            ],
        ),
        migrations.CreateModel(
            name='HitGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('clan_battle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rong.clanbattle')),
            ],
        ),
        migrations.AddField(
            model_name='clanbattlecomp',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rong.hitgroup'),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rong.hitgroup'),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='tags',
            field=models.ManyToManyField(to='rong.HitTag'),
        ),
    ]
