from django.db import models

class ClanCollection(models.Model):
    platform_id = models.CharField(max_length=30, db_index=True)
    name = models.CharField(max_length=50)
    owner = models.ForeignKey('Member', null=True, on_delete=models.SET_NULL)
