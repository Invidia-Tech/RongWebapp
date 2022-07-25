from django.db import models
from django.utils.functional import cached_property

from rong.helpers import primes


class UnitUniqueEquip(models.Model):
    id = models.AutoField(primary_key=True, db_column='equip_id')
    unit = models.OneToOneField('Unit', db_column='unit_id', on_delete=models.DO_NOTHING, related_name='unique_equip')

    class Meta():
        managed = False
        db_table = u'redive_en"."unit_unique_equip'


class Unit(models.Model):
    id = models.AutoField(primary_key=True, db_column='unit_id')
    name = models.TextField(db_column='unit_name')
    cutin_1 = models.IntegerField()
    search_area_width = models.IntegerField()
    rarity = models.IntegerField()

    @cached_property
    def unit_number(self):
        return (self.id - 100001) // 100

    @cached_property
    def prime(self):
        return primes.PRIME_LIST[self.unit_number - 1]

    @cached_property
    def sort_key(self):
        return self.search_area_width * 1000 + self.unit_number

    @cached_property
    def shard_id(self):
        return 30000 + self.id // 100

    @cached_property
    def has_ue(self):
        return hasattr(self, 'unique_equip')

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
    unit = models.ForeignKey('Unit', related_name='ranks', on_delete=models.DO_NOTHING)
    # fake to prevent id column
    promotion_level = models.IntegerField(primary_key=True)
    equip1 = models.IntegerField(db_column='equip_slot_1')
    equip2 = models.IntegerField(db_column='equip_slot_2')
    equip3 = models.IntegerField(db_column='equip_slot_3')
    equip4 = models.IntegerField(db_column='equip_slot_4')
    equip5 = models.IntegerField(db_column='equip_slot_5')
    equip6 = models.IntegerField(db_column='equip_slot_6')

    class Meta():
        managed = False
        db_table = u'redive_en"."unit_promotion'
        ordering = ['promotion_level']


class Equipment(models.Model):
    id = models.IntegerField(primary_key=True, db_column='equipment_id')
    name = models.TextField(db_column='equipment_name')
    promotion_level = models.IntegerField()

    @cached_property
    def refine_stars(self):
        if self.promotion_level >= 4:
            return 5
        elif self.promotion_level == 3:
            return 3
        elif self.promotion_level == 2:
            return 1
        else:
            return 0

    class Meta():
        managed = False
        db_table = u'redive_en"."equipment_data'


class Item(models.Model):
    id = models.IntegerField(primary_key=True, db_column='item_id')
    name = models.TextField(db_column='item_name')
    item_type = models.IntegerField()
    limit_num = models.IntegerField()

    @staticmethod
    def inventory_items():
        return Item.objects.filter(models.Q(item_type=11) | models.Q(id=90005)).order_by('-item_type', 'name')

    class Meta():
        managed = False
        db_table = u'redive_en"."item_data'


class UniqueEquipmentEnhanceData(models.Model):
    enhance_level = models.IntegerField(primary_key=True, db_column='enhance_level')

    class Meta:
        managed = False
        db_table = u'redive_en"."unique_equipment_enhance_data'


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

class StoryDetail(models.Model):
    id = models.IntegerField(primary_key=True, db_column='story_id')
    love_level = models.IntegerField()

    class Meta():
        managed = False
        db_table = u'redive_en"."story_detail'


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

class ENClanBattleMapData2(models.Model):
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
        db_table = u'redive_en"."clan_battle_2_map_data'


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
