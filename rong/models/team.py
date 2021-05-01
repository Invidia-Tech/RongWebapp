from django.db import models

class Team(models.Model):
    power = models.PositiveIntegerField(null=True)
    unit1 = models.ForeignKey('Unit', related_name='unit1teams', on_delete=models.DO_NOTHING)
    unit1_star = models.PositiveIntegerField(null=True)
    unit1_level = models.PositiveIntegerField(null=True)
    unit2 = models.ForeignKey('Unit', related_name='unit2teams', on_delete=models.DO_NOTHING)
    unit2_star = models.PositiveIntegerField(null=True)
    unit2_level = models.PositiveIntegerField(null=True)
    unit3 = models.ForeignKey('Unit', related_name='unit3teams', on_delete=models.DO_NOTHING)
    unit3_star = models.PositiveIntegerField(null=True)
    unit3_level = models.PositiveIntegerField(null=True)
    unit4 = models.ForeignKey('Unit', related_name='unit4teams', on_delete=models.DO_NOTHING)
    unit4_star = models.PositiveIntegerField(null=True)
    unit4_level = models.PositiveIntegerField(null=True)
    unit5 = models.ForeignKey('Unit', related_name='unit5teams', on_delete=models.DO_NOTHING)
    unit5_level = models.PositiveIntegerField(null=True)
    unit5_star = models.PositiveIntegerField(null=True)
