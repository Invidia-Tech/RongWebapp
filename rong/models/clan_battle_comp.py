from django.db import models

class ClanBattleComp(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE)
    submitter = models.ForeignKey('Member', on_delete=models.CASCADE)
    boss_lap = models.IntegerField()
    boss_number = models.IntegerField()
    unit1 = models.ForeignKey('Unit', null=True, on_delete=models.SET_NULL, related_name='unit1comps')
    unit2 = models.ForeignKey('Unit', null=True, on_delete=models.SET_NULL, related_name='unit2comps')
    unit3 = models.ForeignKey('Unit', null=True, on_delete=models.SET_NULL, related_name='unit3comps')
    unit4 = models.ForeignKey('Unit', null=True, on_delete=models.SET_NULL, related_name='unit4comps')
    borrowed_unit = models.ForeignKey('Unit', null=True, on_delete=models.SET_NULL, related_name='borrowedcomps')
    damage = models.IntegerField()
