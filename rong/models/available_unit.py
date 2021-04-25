from django.db import models

class AvailableUnit(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)
    power = models.IntegerField()
    star = models.IntegerField()
    rank = models.IntegerField()
    equip_1 = models.IntegerField()
    equip_2 = models.IntegerField()
    equip_3 = models.IntegerField()
    equip_4 = models.IntegerField()
    equip_5 = models.IntegerField()
