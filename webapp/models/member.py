from django.db import models

class Member(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE, related_name='members')
    platform_id = models.BigIntegerField()
    name = models.CharField(max_length=50)
    is_lead = models.BooleanField()
    group_num = models.IntegerField()
