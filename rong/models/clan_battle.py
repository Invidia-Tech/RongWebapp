from django.db import models

class ClanBattle(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    current_lap = models.PositiveIntegerField(null=True)
    current_boss = models.PositiveIntegerField(null=True)
    current_hp = models.PositiveIntegerField(null=True)

    def lap_info(self, lap):
        return self.bosses.get(models.Q(lap_from__lte=lap) & (models.Q(lap_to__isnull=True) | models.Q(lap_to__gte=lap)))
    
    def spawn_next_boss(self):
        # called from hit when hp=0 to load new boss's hp, doesn't call save itself
        if self.current_boss == 5:
            self.current_lap += 1
        else:
            self.current_boss += 1
        self.current_hp = getattr(self.lap_info(self.current_lap), 'boss%d_hp' % self.current_boss)
    
    def recalculate(self):
        # recalculate all hits starting from scratch
        # used after order or boss data change
        boss_data = list(self.bosses.order_by('difficulty').all())
        difficulty_idx = 0
        self.current_lap = 1
        self.current_boss = 1
        self.current_hp = boss_data[0].boss1_hp
        current_day = 0
        lasthit_users = []
        hits = list(self.hits.order_by('order').all())
        for hit in hits:
            if current_day != hit.day:
                current_day = hit.day
                lasthit_users = []
            hit.boss_lap = self.current_lap
            hit.boss_number = self.current_boss
            hit.actual_damage = min(hit.damage, self.current_hp)
            hit.is_carryover = hit.user_id in lasthit_users
            if hit.is_carryover:
                lasthit_users.remove(hit.user_id)
            hit.is_last_hit = (not hit.is_carryover) and hit.actual_damage == self.current_hp
            if hit.is_last_hit:
                lasthit_users.append(hit.user_id)
            hit.save()
            self.current_hp -= hit.actual_damage
            if self.current_hp == 0:
                if self.current_boss == 5:
                    self.current_lap += 1
                    self.current_boss = 1
                    if boss_data[difficulty_idx].lap_to is not None and boss_data[difficulty_idx].lap_to < self.current_lap:
                        difficulty_idx += 1
                else:
                    self.current_boss += 1
                self.current_hp = getattr(boss_data[difficulty_idx], 'boss%d_hp' % self.current_boss)
        # done
        self.save()
