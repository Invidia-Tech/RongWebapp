from django.db import models

class ClanBattleComp(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE)
    submitter = models.ForeignKey('Member', on_delete=models.CASCADE)
    boss_phase = models.IntegerField()
    boss_number = models.IntegerField()
    unit1 = models.ForeignKey('Unit', null=True, related_name='unit1comps', on_delete=models.DO_NOTHING)
    unit1_star = models.IntegerField(null=True)
    unit2 = models.ForeignKey('Unit', null=True, related_name='unit2comps', on_delete=models.DO_NOTHING)
    unit2_star = models.IntegerField(null=True)
    unit3 = models.ForeignKey('Unit', null=True, related_name='unit3comps', on_delete=models.DO_NOTHING)
    unit3_star = models.IntegerField(null=True)
    unit4 = models.ForeignKey('Unit', null=True, related_name='unit4comps', on_delete=models.DO_NOTHING)
    unit4_star = models.IntegerField(null=True)
    borrowed_unit = models.ForeignKey('Unit', null=True, related_name='borrowedcomps', on_delete=models.DO_NOTHING)
    borrowed_unit_star = models.IntegerField(null=True)
    damage = models.IntegerField()
