# Generated by Django 3.2.3 on 2021-11-27 11:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0060_remove_clan_platform_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='clan',
            name='platform_id',
            field=models.CharField(db_index=True, default='unset', max_length=30),
            preserve_default=False,
        ),
    ]
