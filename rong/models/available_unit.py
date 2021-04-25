from django.db import models

class AvailableUnit(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)
    power = models.IntegerField()
    star = models.IntegerField()
    rank = models.TextField()
