from django.db import models

class BattleArenaCounter(models.Model):
    submitter = models.ForeignKey('Member', null=True, on_delete=models.SET_NULL)
    from_defense = models.BooleanField()
    last_updated = models.DateTimeField()
    upvotes = models.PositiveIntegerField()
    downvotes = models.PositiveIntegerField()
    notes = models.TextField()
    attacker_team = models.OneToOneField('Team', on_delete=models.CASCADE, related_name='attacker_in')
    defender_team = models.OneToOneField('Team', on_delete=models.CASCADE, related_name='defender_in')
