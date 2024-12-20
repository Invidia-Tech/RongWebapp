from django.db import models


class PrincessArenaComp(models.Model):
    name = models.CharField(max_length=20)
    user_id = models.PositiveIntegerField(null=True)
    pfp_unit = models.ForeignKey('Unit', on_delete=models.DO_NOTHING)
    bracket = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    team1 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team1_for')
    team2 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team2_for')
    team3 = models.ForeignKey('Team', null=True, on_delete=models.SET_NULL, related_name='team3_for')
    notes = models.TextField()
