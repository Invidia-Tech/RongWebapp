# Generated by Django 3.2.3 on 2021-11-26 23:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0059_remove_user_single_mode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clan',
            name='platform_id',
        ),
    ]
