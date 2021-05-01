from django.db import models

class Member(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE, related_name='members')
    platform_id = models.CharField(max_length=30, db_index=True)
    name = models.CharField(max_length=50)
    is_lead = models.BooleanField()
    group_num = models.PositiveIntegerField()
