from django.db import models


class ClanBattleComp(models.Model):
    clan_battle = models.ForeignKey('ClanBattle', on_delete=models.CASCADE, related_name='comps')
    name = models.CharField(max_length=50)
    submitter = models.ForeignKey('User', on_delete=models.CASCADE)
    boss_phase = models.PositiveIntegerField()
    boss_number = models.PositiveIntegerField()
    damage = models.PositiveIntegerField()
    team = models.ForeignKey('Team', default=0, on_delete=models.CASCADE)

    def lap_range(self):
        phase_info = self.clan_battle.bosses.get(difficulty=self.boss_phase)
        return [phase_info.lap_from, phase_info.lap_to if phase_info.lap_to is not None else 180]

    def boss(self):
        return chr(0x40 + self.boss_phase) + str(self.boss_number)

    def save(self, *args, **kwargs):
        super(ClanBattleComp, self).save(*args, **kwargs)
        # set and unset matching hits
        lap_info = self.lap_range()
        for hit in self.hits.filter(comp_locked=False).select_related('team'):
            unlink = False
            if hit.boss_lap < lap_info[0] or hit.boss_lap > lap_info[1] or hit.boss_number != self.boss_number:
                unlink = True
            if hit.team and hit.team.uid != self.team.uid:
                unlink = True
            if unlink:
                hit.comp = None
                hit.save()

        for hit in self.clan_battle.hits.filter(boss_lap__gte=lap_info[0], boss_lap__lte=lap_info[1],
                                                boss_number=self.boss_number, comp_locked=False).select_related('team'):
            if hit.team and hit.team.uid == self.team.uid:
                hit.comp = self
                hit.save()
