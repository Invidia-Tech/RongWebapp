# Generated by Django 3.2.3 on 2021-06-03 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0030_remove_team_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='uid',
            field=models.BigIntegerField(db_index=True, default=0),
            preserve_default=False,
        ),
    ]