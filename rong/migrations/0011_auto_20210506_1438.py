# Generated by Django 3.2 on 2021-05-06 02:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0010_clanmember_box'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='battlearenacounter',
            name='last_updated',
        ),
        migrations.AddField(
            model_name='battlearenacounter',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='battlearenacounter',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AddField(
            model_name='princessarenacomp',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='princessarenacomp',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
