from django.db import models
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField

from rong.models.clan_battle_boss_info import ClanBattleBossInfo
from rong.models.redive_models import CNClanBattleMapData, CNClanBattlePeriod, CNEnemyParameter, CNWaveGroupData, \
    ENClanBattleBossGroup, ENClanBattleMapData, ENClanBattlePeriod, EnemyParameter, JPClanBattleMapData, \
    JPClanBattlePeriod, JPEnemyParameter, JPWaveGroupData, WaveGroupData
from .clan_battle_score import ClanBattleHitType

CB_DATA_SOURCES = [
    {
        "prefix": "en",
        "name": "Global Server",
        "periodModel": ENClanBattlePeriod,
        "mapModel": ENClanBattleMapData,
        "dataType": "old",
        "bossGroupModel": ENClanBattleBossGroup,
        "waveGroupModel": WaveGroupData,
        "enemyModel": EnemyParameter
    },
    {
        "prefix": "jp",
        "name": "JP Server",
        "periodModel": JPClanBattlePeriod,
        "mapModel": JPClanBattleMapData,
        "dataType": "new",
        "waveGroupModel": JPWaveGroupData,
        "enemyModel": JPEnemyParameter
    },
    {
        "prefix": "cn",
        "name": "CN Server",
        "periodModel": CNClanBattlePeriod,
        "mapModel": CNClanBattleMapData,
        "dataType": "new",
        "waveGroupModel": CNWaveGroupData,
        "enemyModel": CNEnemyParameter
    }
]


class ClanBattle(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from=['clan__name', 'name'], unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    boss1_name = models.CharField(max_length=50)
    boss2_name = models.CharField(max_length=50)
    boss3_name = models.CharField(max_length=50)
    boss4_name = models.CharField(max_length=50)
    boss5_name = models.CharField(max_length=50)
    boss1_iconid = models.PositiveIntegerField(null=True)
    boss2_iconid = models.PositiveIntegerField(null=True)
    boss3_iconid = models.PositiveIntegerField(null=True)
    boss4_iconid = models.PositiveIntegerField(null=True)
    boss5_iconid = models.PositiveIntegerField(null=True)
    current_lap = models.PositiveIntegerField(null=True)
    current_boss = models.PositiveIntegerField(null=True)
    current_hp = models.PositiveIntegerField(null=True)

    def _load_boss(self, map_info, boss_index, enemy_data, multiplier, force_load_names):
        field_prefix = 'boss%d_' % (boss_index + 1)
        map_info.populate_boss(boss_index + 1, enemy_data, multiplier)
        setattr(self, field_prefix + 'iconid', enemy_data.unit_id)

        if not getattr(self, field_prefix + 'name') or force_load_names:
            setattr(self, field_prefix + 'name', enemy_data.name)

    def load_boss_info(self, source: str, force_load_names: bool = False):
        try:
            source_info = [
                si for si in CB_DATA_SOURCES if source.startswith(si["prefix"])][0]
        except:
            raise ValueError("Unknown CB source")
        cb_id = int(source[source.index("-") + 1:])
        map_entries = source_info["mapModel"].objects.filter(
            id=cb_id).order_by('lap_num_from')
        self.bosses.all().delete()
        map_info = None
        last_id = None
        difficulty = 1
        for map_entry in map_entries:
            if source_info["dataType"] == "old":
                if last_id == map_entry.boss_group_id:
                    # identical boss info and scoring, so this only changed rewards
                    # we don't care about rewards - so collapse this row into the last
                    map_info.lap_to = None if map_entry.lap_num_to == -1 else map_entry.lap_num_to
                    map_info.save()
                else:
                    # make a new entry
                    map_info = ClanBattleBossInfo(
                        clan_battle=self,
                        difficulty=difficulty,
                        lap_from=map_entry.lap_num_from,
                        lap_to=None if map_entry.lap_num_to == -1 else map_entry.lap_num_to
                    )

                    # populate boss info
                    boss_groups = list(source_info["bossGroupModel"].objects.filter(
                        id=map_entry.boss_group_id).order_by('order_num'))
                    for boss_index, boss_group in enumerate(boss_groups):
                        wave_group = source_info["waveGroupModel"].objects.get(
                            id=boss_group.wave_group_id)
                        enemy_data = source_info["enemyModel"].objects.get(
                            id=wave_group.enemy_id_1)
                        self._load_boss(map_info, boss_index, enemy_data, boss_group.score_coefficient,
                                        force_load_names)

                    map_info.save()
                    difficulty += 1
                    last_id = map_entry.boss_group_id
            else:
                # new data
                curr_boss_id_mults = []
                for boss in range(5):
                    curr_boss_id_mults += [getattr(map_entry, 'wave_group_id_%d' % (
                            boss + 1)), getattr(map_entry, 'score_coefficient_%d' % (boss + 1))]

                if curr_boss_id_mults == last_id:
                    # identical boss info and scoring, so this only changed rewards
                    # we don't care about rewards - so collapse this row into the last
                    map_info.lap_to = None if map_entry.lap_num_to == -1 else map_entry.lap_num_to
                    map_info.save()
                else:
                    # make a new entry
                    map_info = ClanBattleBossInfo(
                        clan_battle=self,
                        difficulty=difficulty,
                        lap_from=map_entry.lap_num_from,
                        lap_to=None if map_entry.lap_num_to == -1 else map_entry.lap_num_to
                    )

                    # populate boss info
                    for boss_index in range(5):
                        wave_group = source_info["waveGroupModel"].objects.get(
                            id=curr_boss_id_mults[boss_index * 2])
                        enemy_data = source_info["enemyModel"].objects.get(
                            id=wave_group.enemy_id_1)
                        self._load_boss(map_info, boss_index, enemy_data, curr_boss_id_mults[boss_index * 2 + 1],
                                        force_load_names)

                    map_info.save()
                    difficulty += 1
                    last_id = curr_boss_id_mults

    def lap_info(self, lap):
        return self.bosses.get(
            models.Q(lap_from__lte=lap) & (models.Q(lap_to__isnull=True) | models.Q(lap_to__gte=lap)))

    def spawn_next_boss(self):
        # called from hit when hp=0 to load new boss's hp, doesn't call save itself
        if self.current_boss == 5:
            self.current_lap += 1
            self.current_boss = 1
        else:
            self.current_boss += 1
        self.current_hp = getattr(self.lap_info(
            self.current_lap), 'boss%d_hp' % self.current_boss)

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
            if hit.user_id in lasthit_users:
                hit.hit_type = ClanBattleHitType.CARRYOVER
                lasthit_users.remove(hit.user_id)
            elif hit.actual_damage == self.current_hp:
                hit.hit_type = ClanBattleHitType.LAST_HIT
                lasthit_users.append(hit.user_id)
            else:
                hit.hit_type = ClanBattleHitType.NORMAL
            hit.save()
            self.current_hp -= hit.actual_damage
            if self.current_hp == 0:
                if self.current_boss == 5:
                    self.current_lap += 1
                    self.current_boss = 1
                    if boss_data[difficulty_idx].lap_to is not None and boss_data[
                        difficulty_idx].lap_to < self.current_lap:
                        difficulty_idx += 1
                else:
                    self.current_boss += 1
                self.current_hp = getattr(
                    boss_data[difficulty_idx], 'boss%d_hp' % self.current_boss)
        # done
        self.save()

    def get_clan_id(self):
        return self.clan_id

    @property
    def in_progress(self):
        now = timezone.now()
        return self.start_time <= now and self.end_time > now
