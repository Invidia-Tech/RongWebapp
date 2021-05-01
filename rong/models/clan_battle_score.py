from django.db import models

class ClanBattleScore(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE)
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    boss_lap = models.PositiveIntegerField()
    boss_number = models.PositiveIntegerField()
    damage = models.PositiveIntegerField()
    team = models.OneToOneField('Team', null=True, on_delete=models.SET_NULL)
    unit1_damage = models.PositiveIntegerField(null=True)
    unit2_damage = models.PositiveIntegerField(null=True)
    unit3_damage = models.PositiveIntegerField(null=True)
    unit4_damage = models.PositiveIntegerField(null=True)
    unit5_damage = models.PositiveIntegerField(null=True)
