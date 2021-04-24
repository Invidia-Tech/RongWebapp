from django.db import models

class ClanCollection(models.Model):
    guild_id = models.BigIntegerField()
    name = models.CharField(max_length=50)
    owner = models.ForeignKey('Member', null=True, on_delete=models.SET_NULL)
