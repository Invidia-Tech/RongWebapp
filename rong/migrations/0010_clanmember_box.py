# Generated by Django 3.2 on 2021-05-05 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0009_alter_clanmember_group_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='clanmember',
            name='box',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rong.box'),
        ),
    ]
