# Generated by Django 3.2 on 2021-05-06 02:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0011_auto_20210506_1438'),
    ]

    operations = [
        migrations.RenameField(
            model_name='princessarenacomp',
            old_name='last_updated',
            new_name='updated_at',
        ),
    ]
