from django.db import models


class HitTag(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE, related_name='hit_tags')
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
