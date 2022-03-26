from django.db import models


class ClanBattleComp(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    submitter = models.ForeignKey('User', on_delete=models.CASCADE)
    boss_phase = models.PositiveIntegerField()
    boss_number = models.PositiveIntegerField()
    damage = models.PositiveIntegerField()
    team = models.ForeignKey('Team', default=0, on_delete=models.CASCADE)
