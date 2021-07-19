from django.db import models


class BattleArenaCounter(models.Model):
    submitter = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    from_defense = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    upvotes = models.PositiveIntegerField()
    downvotes = models.PositiveIntegerField()
    notes = models.TextField()
    attacker_team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='attacker_in')
    defender_team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='defender_in')
