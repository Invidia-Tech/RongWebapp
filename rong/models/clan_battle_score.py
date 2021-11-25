from enum import Enum

from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property
from django.utils.html import format_html
from django_enum_choices.fields import EnumChoiceField


class ClanBattleHitType(Enum):
    NORMAL = "Normal"
    LAST_HIT = "Last Hit"
    CARRYOVER = "Carryover"


class ClanBattleScore(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE, related_name='hits')
    member = models.ForeignKey('ClanMember', on_delete=models.CASCADE, null=True)
    day = models.PositiveIntegerField()
    damage = models.PositiveIntegerField()
    team = models.ForeignKey('Team', null=True, on_delete=models.SET_NULL)
    order = models.PositiveIntegerField()
    unit1_damage = models.PositiveIntegerField(null=True)
    unit2_damage = models.PositiveIntegerField(null=True)
    unit3_damage = models.PositiveIntegerField(null=True)
    unit4_damage = models.PositiveIntegerField(null=True)
    unit5_damage = models.PositiveIntegerField(null=True)
    group = models.ForeignKey('HitGroup', null=True, on_delete=models.SET_NULL, related_name='hits')
    tags = models.ManyToManyField('HitTag', related_name='hits')
    # these fields are autocalculated by the code and shouldn't be filled manually
    boss_lap = models.PositiveIntegerField()
    boss_number = models.PositiveIntegerField()
    actual_damage = models.PositiveIntegerField()
    boss_hp_left = models.PositiveIntegerField()
    hit_type = EnumChoiceField(ClanBattleHitType, default=ClanBattleHitType.NORMAL)
    kyaru_date = models.CharField(max_length=50, null=True)
    kyaru_author = models.CharField(max_length=50, null=True)
    kyaru_image_url = models.TextField(null=True)
    kyaru_boss_number = models.PositiveIntegerField(null=True)

    def clear_unit_damage(self):
        for unit in range(1, 6):
            setattr(self, "unit%d_damage" % unit, None)

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
            previous_hit_today = self.clan_battle.hits.filter(day=self.day, member=self.member).order_by('-order').first()
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

    @cached_property
    def displayed_username(self):
        if self.member.user:
            return format_html('<span title="{}">{}</span>', self.member.user.plaindiscordname, self.member.ign)
        else:
            return self.member.ign

    @cached_property
    def killing_blow(self):
        return self.boss_hp_left == 0
