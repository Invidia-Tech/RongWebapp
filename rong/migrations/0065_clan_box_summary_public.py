# Generated by Django 3.2.3 on 2022-03-09 09:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0064_auto_20211214_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='clan',
            name='box_summary_public',
            field=models.BooleanField(default=False),
        ),
    ]
