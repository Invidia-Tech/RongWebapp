# Generated by Django 3.2.3 on 2021-06-20 10:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0042_clanbattlescore_killing_blow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clanbattlebossinfo',
            options={'ordering': ('difficulty',)},
        ),
        migrations.RemoveField(
            model_name='clanbattlescore',
            name='killing_blow',
        ),
        migrations.AddField(
            model_name='clanbattlescore',
            name='boss_hp_left',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
