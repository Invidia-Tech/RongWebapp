# Generated by Django 3.2.3 on 2021-06-22 08:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0043_auto_20210620_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='clanbattlescore',
            name='ign',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
