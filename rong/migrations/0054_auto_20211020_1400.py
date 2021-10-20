# Generated by Django 3.2.3 on 2021-10-20 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rong', '0053_auto_20211009_0852'),
    ]

    operations = [
        migrations.AddField(
            model_name='clanbattlescore',
            name='kyaru_author',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='kyaru_boss_number',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='kyaru_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='kyaru_image_url',
            field=models.TextField(null=True),
        ),
    ]
