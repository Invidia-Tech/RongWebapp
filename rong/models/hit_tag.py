from django.db import models


class HitTag(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.TextField()
