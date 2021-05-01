from django.db import models

class AvailableUnit(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)
    power = models.PositiveIntegerField(null=True)
    level = models.PositiveIntegerField(null=True)
    star = models.PositiveIntegerField(null=True)
    rank = models.PositiveIntegerField(null=True)
    bond = models.PositiveIntegerField(null=True)
    # null = unequipped or not specified, 0-5 = refinement stars
    equip1 = models.PositiveIntegerField(null=True)
    equip2 = models.PositiveIntegerField(null=True)
    equip3 = models.PositiveIntegerField(null=True)
    equip4 = models.PositiveIntegerField(null=True)
    equip5 = models.PositiveIntegerField(null=True)
    equip6 = models.PositiveIntegerField(null=True)
