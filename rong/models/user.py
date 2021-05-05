from django.db import models

class User(models.Model):
    platform_id = models.CharField(max_length=30, db_index=True)
    name = models.CharField(max_length=50)
    clans = models.ManyToManyField('Clan', through='ClanMember')
