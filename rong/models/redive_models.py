from django.db import models


class Unit(models.Model):
    id = models.AutoField(primary_key=True, db_column='unit_id')
    name = models.TextField(db_column='unit_name')
    cutin_1 = models.IntegerField()
    search_area_width = models.IntegerField()
    rarity = models.IntegerField()

    @staticmethod
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
    # fake to prevent id column
    unit_id = models.IntegerField(primary_key=True)
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


class WaveGroupData(models.Model):
    id = models.IntegerField(primary_key=True, db_column='wave_group_id')
    odds = models.IntegerField()
    enemy_id_1 = models.IntegerField()

    class Meta():
        managed = False
        db_table = u'redive_en"."wave_group_data'


class EnemyParameter(models.Model):
    id = models.IntegerField(primary_key=True, db_column='enemy_id')
    unit_id = models.IntegerField()
    name = models.TextField()
    level = models.IntegerField()
    hp = models.IntegerField()
    pdef = models.IntegerField(db_column='def')
    mdef = models.IntegerField(db_column='magic_def')

    class Meta():
        managed = False
        db_table = u'redive_en"."enemy_parameter'


class ENClanBattlePeriod(models.Model):
    id = models.IntegerField(primary_key=True, db_column='clan_battle_id')
    start_time = models.TextField()
    end_time = models.TextField()

    class Meta():
        managed = False
        db_table = u'redive_en"."clan_battle_period'


class ENClanBattleMapData(models.Model):
    id = models.IntegerField(primary_key=True, db_column='clan_battle_id')
    lap_num_from = models.IntegerField()
    lap_num_to = models.IntegerField()
    boss_group_id = models.IntegerField(db_column='clan_battle_boss_group_id')

    class Meta():
        managed = False
        db_table = u'redive_en"."clan_battle_map_data'


class ENClanBattleBossGroup(models.Model):
    id = models.IntegerField(
        primary_key=True, db_column='clan_battle_boss_group_id')
    order_num = models.IntegerField()
    wave_group_id = models.IntegerField()
    score_coefficient = models.FloatField()

    class Meta():
        managed = False
        db_table = u'redive_en"."clan_battle_boss_group'


class JPClanBattlePeriod(models.Model):
    id = models.IntegerField(primary_key=True, db_column='clan_battle_id')
    start_time = models.TextField()
    end_time = models.TextField()

    class Meta():
        managed = False
        db_table = u'redive_jp"."clan_battle_period'


class JPClanBattleMapData(models.Model):
    id = models.IntegerField(primary_key=True, db_column='clan_battle_id')
    lap_num_from = models.IntegerField()
    lap_num_to = models.IntegerField()
    wave_group_id_1 = models.IntegerField()
    score_coefficient_1 = models.FloatField()
    wave_group_id_2 = models.IntegerField()
    score_coefficient_2 = models.FloatField()
    wave_group_id_3 = models.IntegerField()
    score_coefficient_3 = models.FloatField()
    wave_group_id_4 = models.IntegerField()
    score_coefficient_4 = models.FloatField()
    wave_group_id_5 = models.IntegerField()
    score_coefficient_5 = models.FloatField()

    class Meta():
        managed = False
        db_table = u'redive_jp"."clan_battle_2_map_data'


class JPWaveGroupData(models.Model):
    id = models.IntegerField(primary_key=True, db_column='wave_group_id')
    odds = models.IntegerField()
    enemy_id_1 = models.IntegerField()

    class Meta():
        managed = False
        db_table = u'redive_jp"."wave_group_data'


class JPEnemyParameter(models.Model):
    id = models.IntegerField(primary_key=True, db_column='enemy_id')
    unit_id = models.IntegerField()
    name = models.TextField()
    level = models.IntegerField()
    hp = models.IntegerField()
    pdef = models.IntegerField(db_column='def')
    mdef = models.IntegerField(db_column='magic_def')

    class Meta():
        managed = False
        db_table = u'redive_jp"."enemy_parameter'


class CNClanBattlePeriod(models.Model):
    id = models.IntegerField(primary_key=True, db_column='clan_battle_id')
    start_time = models.TextField()
    end_time = models.TextField()

    class Meta():
        managed = False
        db_table = u'redive_cn"."clan_battle_period'


class CNClanBattleMapData(models.Model):
    id = models.IntegerField(primary_key=True, db_column='clan_battle_id')
    lap_num_from = models.IntegerField()
    lap_num_to = models.IntegerField()
    wave_group_id_1 = models.IntegerField()
    score_coefficient_1 = models.FloatField()
    wave_group_id_2 = models.IntegerField()
    score_coefficient_2 = models.FloatField()
    wave_group_id_3 = models.IntegerField()
    score_coefficient_3 = models.FloatField()
    wave_group_id_4 = models.IntegerField()
    score_coefficient_4 = models.FloatField()
    wave_group_id_5 = models.IntegerField()
    score_coefficient_5 = models.FloatField()

    class Meta():
        managed = False
        db_table = u'redive_cn"."clan_battle_2_map_data'


class CNWaveGroupData(models.Model):
    id = models.IntegerField(primary_key=True, db_column='wave_group_id')
    odds = models.IntegerField()
    enemy_id_1 = models.IntegerField()

    class Meta():
        managed = False
        db_table = u'redive_cn"."wave_group_data'


class CNEnemyParameter(models.Model):
    id = models.IntegerField(primary_key=True, db_column='enemy_id')
    unit_id = models.IntegerField()
    name = models.TextField()
    level = models.IntegerField()
    hp = models.IntegerField()
    pdef = models.IntegerField(db_column='def')
    mdef = models.IntegerField(db_column='magic_def')

    class Meta():
        managed = False
        db_table = u'redive_cn"."enemy_parameter'
