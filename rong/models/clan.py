from django.db import models
from django_extensions.db.fields import AutoSlugField


class Clan(models.Model):
    collection = models.ForeignKey('ClanCollection', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    platform_id = models.CharField(max_length=30, db_index=True)
    admin = models.ForeignKey(
        'User', null=True, on_delete=models.SET_NULL, related_name='clans_administrated')
    members = models.ManyToManyField('User', through='ClanMember')
    slug = AutoSlugField(populate_from='name', unique=True)

    def get_clan_id(self):
        return self.id
