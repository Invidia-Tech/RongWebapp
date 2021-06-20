from enum import Enum

from django.db import models
from django.db.models import Max
from django_enum_choices.fields import EnumChoiceField


class ClanBattleHitType(Enum):
    NORMAL = "Normal"
    LAST_HIT = "Last Hit"
    CARRYOVER = "Carryover"


class ClanBattleScore(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE, related_name='hits')
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    day = models.PositiveIntegerField()
    damage = models.PositiveIntegerField()
    team = models.OneToOneField('Team', null=True, on_delete=models.SET_NULL)
    order = models.PositiveIntegerField()
    unit1_damage = models.PositiveIntegerField(null=True)
    unit2_damage = models.PositiveIntegerField(null=True)
    unit3_damage = models.PositiveIntegerField(null=True)
    unit4_damage = models.PositiveIntegerField(null=True)
    unit5_damage = models.PositiveIntegerField(null=True)
    # these fields are autocalculated by the code and shouldn't be filled manually
    boss_lap = models.PositiveIntegerField()
    boss_number = models.PositiveIntegerField()
    actual_damage = models.PositiveIntegerField()
    boss_hp_left = models.PositiveIntegerField()
    hit_type = EnumChoiceField(ClanBattleHitType, default=ClanBattleHitType.NORMAL)

    def save(self, *args, **kwargs):
        # autopopulate fields for new entry
        if self.order is None or self.order <= 0:
            self.order = (self.clan_battle.hits.aggregate(Max('order'))['order__max'] or 0) + 1
            if self.clan_battle.current_lap is None:
                # first hit, start the CB
                self.clan_battle.current_lap = 1
                self.clan_battle.current_boss = 1
                self.clan_battle.current_hp = self.clan_battle.lap_info(1).boss1_hp
            # now deal with the hit
            self.boss_lap = self.clan_battle.current_lap
            self.boss_number = self.clan_battle.current_boss
            self.actual_damage = min(self.damage, self.clan_battle.current_hp)
            previous_hit_today = self.clan_battle.hits.filter(day=self.day, user=self.user).order_by('-order').first()
            if previous_hit_today and previous_hit_today.hit_type == ClanBattleHitType.LAST_HIT:
                self.hit_type = ClanBattleHitType.CARRYOVER
            elif self.actual_damage == self.clan_battle.current_hp:
                self.hit_type = ClanBattleHitType.LAST_HIT
            else:
                self.hit_type = ClanBattleHitType.NORMAL
            self.clan_battle.current_hp -= self.actual_damage
            self.boss_hp_left = self.clan_battle.current_hp
            if self.clan_battle.current_hp == 0:
                self.clan_battle.spawn_next_boss()
            self.clan_battle.save()
        super().save(*args, **kwargs)
