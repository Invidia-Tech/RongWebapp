from django.db import models

class Unit(models.Model):
    id = models.AutoField(primary_key=True, db_column='unit_id')
    name = models.TextField(db_column='unit_name')

    class Meta():
        managed = False
        db_table = u'redive_en"."unit_data'

class ClanBattleSchedule(models.Model):
    id = models.AutoField(primary_key=True, db_column='clan_battle_id')
    release_month = models.IntegerField()
    last_cb = models.IntegerField(db_column='last_clan_battle_id')
    start_time = models.TextField()
    end_time = models.TextField()

    class Meta():
        managed = False
        db_table = u'redive_en"."clan_battle_schedule'
