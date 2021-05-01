from django.db import models

class ClanBattleComp(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE)
    submitter = models.ForeignKey('Member', on_delete=models.CASCADE)
    boss_phase = models.PositiveIntegerField()
    boss_number = models.PositiveIntegerField()
    damage = models.PositiveIntegerField()
    team = models.OneToOneField('Team', default=0, on_delete=models.CASCADE)
    borrowed_unit = models.PositiveIntegerField(null=True)
