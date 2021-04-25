from django.db import models

class ClanBattleScore(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE)
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    boss_lap = models.IntegerField()
    boss_number = models.IntegerField()
    damage = models.IntegerField()
