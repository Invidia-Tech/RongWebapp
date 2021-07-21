from django.db import models


class HitGroup(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE, related_name='hit_groups')
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)


