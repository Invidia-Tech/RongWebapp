from django.db import models

class Clan(models.Model):
    collection = models.ForeignKey('ClanCollection', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    role_id = models.CharField(max_length=30, db_index=True)
    admin = models.ForeignKey('Member', null=True, on_delete=models.SET_NULL, related_name='clans_administrated')