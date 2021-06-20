from django.db import models


class ClanBattleBossInfo(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE, related_name='bosses')
    difficulty = models.PositiveIntegerField()
    lap_from = models.PositiveIntegerField()
    lap_to = models.PositiveIntegerField(null=True)
    boss1_level = models.PositiveIntegerField()
    boss1_multiplier = models.DecimalField(max_digits=3, decimal_places=2)
    boss1_hp = models.PositiveIntegerField()
    boss1_pdef = models.PositiveIntegerField()
    boss1_mdef = models.PositiveIntegerField()
    boss2_level = models.PositiveIntegerField()
    boss2_multiplier = models.DecimalField(max_digits=3, decimal_places=2)
    boss2_hp = models.PositiveIntegerField()
    boss2_pdef = models.PositiveIntegerField()
    boss2_mdef = models.PositiveIntegerField()
    boss3_level = models.PositiveIntegerField()
    boss3_multiplier = models.DecimalField(max_digits=3, decimal_places=2)
    boss3_hp = models.PositiveIntegerField()
    boss3_pdef = models.PositiveIntegerField()
    boss3_mdef = models.PositiveIntegerField()
    boss4_level = models.PositiveIntegerField()
    boss4_multiplier = models.DecimalField(max_digits=3, decimal_places=2)
    boss4_hp = models.PositiveIntegerField()
    boss4_pdef = models.PositiveIntegerField()
    boss4_mdef = models.PositiveIntegerField()
    boss5_level = models.PositiveIntegerField()
    boss5_multiplier = models.DecimalField(max_digits=3, decimal_places=2)
    boss5_hp = models.PositiveIntegerField()
    boss5_pdef = models.PositiveIntegerField()
    boss5_mdef = models.PositiveIntegerField()

    def populate_boss(self, boss_num, enemy_data, multiplier):
        field_prefix = 'boss%d_' % boss_num
        setattr(self, field_prefix + 'level', enemy_data.level)
        setattr(self, field_prefix + 'hp', enemy_data.hp)
        setattr(self, field_prefix + 'pdef', enemy_data.pdef)
        setattr(self, field_prefix + 'mdef', enemy_data.mdef)
        setattr(self, field_prefix + 'multiplier', multiplier)

    def boss_list(self):
        boss_l = []
        for num in range(1, 6):
            boss_l.append({
                "level": getattr(self, 'boss%d_level' % num),
                "hp": getattr(self, 'boss%d_hp' % num),
                "multiplier": getattr(self, 'boss%d_multiplier' % num),
                "pdef": getattr(self, 'boss%d_pdef' % num),
                "mdef": getattr(self, 'boss%d_mdef' % num),
            })
        return boss_l

    class Meta:
        ordering = ('difficulty',)
