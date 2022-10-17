# Generated by Django 3.2.3 on 2021-11-25 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('rong', '0056_auto_20211126_0513'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='clanmember',
            name='unique user clan',
        ),
        migrations.AlterField(
            model_name='clanmember',
            name='ign',
            field=models.CharField(default='Unnamed', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clanmember',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='all_clan_memberships', to='rong.user'),
        ),
    ]
