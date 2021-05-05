from django.db import models

class MemberSchedule(models.Model):
    member = models.ForeignKey('ClanMember', on_delete=models.CASCADE)
    time_available = models.TimeField()
    available_length = models.DurationField()
