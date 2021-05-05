from django.db import models

class ClanMember(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE)
    is_lead = models.BooleanField()
    group_num = models.PositiveIntegerField(null=True)
    box = models.OneToOneField('Box', null=True, on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'clan'], name='unique user clan')
        ]
