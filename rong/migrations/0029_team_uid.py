# Generated by Django 3.2 on 2021-06-02 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0028_rename_begin_time_clanbattle_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='uid',
            field=models.CharField(db_index=True, default='', max_length=40),
            preserve_default=False,
        ),
    ]
