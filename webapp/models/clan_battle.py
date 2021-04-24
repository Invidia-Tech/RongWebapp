from django.db import models

class ClanBattle(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    game_id = models.ForeignKey('ClanBattleSchedule', null=True, on_delete=models.SET_NULL)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
