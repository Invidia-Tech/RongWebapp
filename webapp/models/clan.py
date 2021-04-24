from django.db import models

class Clan(models.Model):
    collection = models.ForeignKey('ClanCollection', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    role_id = models.BigIntegerField()
    admin = models.ForeignKey('Member', null=True, on_delete=models.SET_NULL, related_name='clans_administrated')