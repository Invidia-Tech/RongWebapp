# Generated by Django 3.2.3 on 2021-06-03 05:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0029_team_uid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='uid',
        ),
    ]
