from django.db import models

class Unit(models.Model):
    id = models.AutoField(primary_key=True, db_column='unit_id')
    name = models.TextField(db_column='unit_name')
    cutin_1 = models.IntegerField()
    search_area_width = models.IntegerField()
    rarity = models.IntegerField()

    def valid_units():
        return Unit.objects.filter(id__gt=100000, id__lt=200000).exclude(cutin_1=0)

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

class SkillCost(models.Model):
    target_level = models.IntegerField(primary_key=True)
    cost = models.IntegerField()

    class Meta():
        managed = False
        db_table = u'redive_en"."skill_cost'

class UnitPromotion(models.Model):
    unit_id = models.IntegerField(primary_key=True) # fake to prevent id column
    promotion_level = models.IntegerField()
    equip1 = models.IntegerField(db_column='equip_slot_1')
    equip2 = models.IntegerField(db_column='equip_slot_2')
    equip3 = models.IntegerField(db_column='equip_slot_3')
    equip4 = models.IntegerField(db_column='equip_slot_4')
    equip5 = models.IntegerField(db_column='equip_slot_5')
    equip6 = models.IntegerField(db_column='equip_slot_6')

    class Meta():
        managed = False
        db_table = u'redive_en"."unit_promotion'

class Equipment(models.Model):
    id = models.IntegerField(primary_key=True, db_column='equipment_id')
    name = models.TextField(db_column='equipment_name')
    promotion_level = models.IntegerField()

    class Meta():
        managed = False
        db_table = u'redive_en"."equipment_data'
