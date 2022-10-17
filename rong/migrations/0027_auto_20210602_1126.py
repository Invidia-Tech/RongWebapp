# Generated by Django 3.2 on 2021-06-01 23:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0026_cbtables2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clanbattlebossinfo',
            name='boss1_name',
        ),
        migrations.RemoveField(
            model_name='clanbattlebossinfo',
            name='boss2_name',
        ),
        migrations.RemoveField(
            model_name='clanbattlebossinfo',
            name='boss3_name',
        ),
        migrations.RemoveField(
            model_name='clanbattlebossinfo',
            name='boss4_name',
        ),
        migrations.RemoveField(
            model_name='clanbattlebossinfo',
            name='boss5_name',
        ),
        migrations.AddField(
            model_name='clanbattle',
            name='boss1_name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattle',
            name='boss2_name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattle',
            name='boss3_name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattle',
            name='boss4_name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clanbattle',
            name='boss5_name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
