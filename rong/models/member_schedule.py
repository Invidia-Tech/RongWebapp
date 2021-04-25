from django.db import models

class MemberSchedule(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    time_available = models.TextField()
    available_length = models.TextField()
