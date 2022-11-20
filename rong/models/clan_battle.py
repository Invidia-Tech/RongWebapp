import datetime
import math
import statistics
from collections import OrderedDict, defaultdict

from django.db import models, connection
from django.db.models import Sum
from django.utils import timezone
from django.utils.functional import cached_property
from django_extensions.db.fields import AutoSlugField

from rong.models.clan_battle_boss_info import ClanBattleBossInfo
from rong.models.redive_models import CNClanBattleMapData, CNClanBattlePeriod, CNEnemyParameter, CNWaveGroupData, \
    ENClanBattleMapData2, ENClanBattlePeriod, EnemyParameter, JPClanBattleMapData, \
    JPClanBattlePeriod, JPEnemyParameter, JPWaveGroupData, WaveGroupData
from .clan_battle_score import ClanBattleHitType

CB_DATA_SOURCES = [
    {
        "prefix": "en",
        "name": "Global Server",
        "periodModel": ENClanBattlePeriod,
        "mapModel": ENClanBattleMapData2,
        "dataType": "new",
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
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    boss1_name = models.CharField(max_length=50, blank=True)
    boss2_name = models.CharField(max_length=50, blank=True)
    boss3_name = models.CharField(max_length=50, blank=True)
    boss4_name = models.CharField(max_length=50, blank=True)
    boss5_name = models.CharField(max_length=50, blank=True)
    boss1_iconid = models.PositiveIntegerField(null=True)
    boss2_iconid = models.PositiveIntegerField(null=True)
    boss3_iconid = models.PositiveIntegerField(null=True)
    boss4_iconid = models.PositiveIntegerField(null=True)
    boss5_iconid = models.PositiveIntegerField(null=True)
    current_lap = models.PositiveIntegerField(null=True)
    current_boss = models.PositiveIntegerField(null=True)
    current_hp = models.PositiveIntegerField(null=True)
    viewable_by_members = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    HITS_PER_DAY = 3

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
                boss_groups = [{"wave_group": bg.wave_group_id, "multiplier": bg.score_coefficient} for bg in
                               source_info["bossGroupModel"].objects.filter(
                                   id=map_entry.boss_group_id).order_by('order_num')]
            else:
                boss_groups = [{"wave_group": getattr(map_entry, 'wave_group_id_%d' % (i + 1)),
                                "multiplier": getattr(map_entry, 'score_coefficient_%d' % (i + 1))} for i in
                               range(5)]
            current_id = source_info["waveGroupModel"].objects.get(id=boss_groups[0]["wave_group"]).enemy_id_1
            assert len(boss_groups) == 5

            if current_id == last_id:
                # identical boss info and scoring, so this only changed rewards
                # we don't care about rewards - so collapse this row into the last
                map_info.lap_to = None if map_entry.lap_num_to == -1 else map_entry.lap_num_to
                map_info.save()
            else:
                # new entry
                map_info = ClanBattleBossInfo(
                    clan_battle=self,
                    difficulty=difficulty,
                    lap_from=map_entry.lap_num_from,
                    lap_to=None if map_entry.lap_num_to == -1 else map_entry.lap_num_to
                )

                for boss_index, boss_group in enumerate(boss_groups):
                    wave_group = source_info["waveGroupModel"].objects.get(id=boss_group["wave_group"])
                    enemy_data = source_info["enemyModel"].objects.get(
                        id=wave_group.enemy_id_1)
                    field_prefix = 'boss%d_' % (boss_index + 1)
                    map_info.populate_boss(boss_index + 1, enemy_data, boss_group["multiplier"])
                    setattr(self, field_prefix + 'iconid', enemy_data.unit_id)

                    if not getattr(self, field_prefix + 'name') or force_load_names:
                        setattr(self, field_prefix + 'name', enemy_data.name)

                map_info.save()
                difficulty += 1
                last_id = current_id

    def can_be_viewed_by(self, user):
        # Leads can always view CBs.
        if self.clan_id in user.managed_clan_ids:
            return True
        # Members can never view hidden CBs.
        if not self.viewable_by_members:
            return False
        # Otherwise, members can only see CBs if either of the following is true:
        # * The CB has not finished yet or is undated.
        # * They did at least one hit in the CB.
        # They must also be a current member of the clan,
        # aka you can't see historical data from clans you've left for now.
        if not user.in_clan(self.clan):
            return False
        if self.start_time is None or self.end_time > timezone.now():
            return True
        return user.participated_in(self)

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
        has_manual_hits = self.hits.filter(ingame_timestamp=None).exists()
        difficulty_idx = 0
        self.current_lap = 1
        self.current_boss = 1
        self.current_hp = boss_data[0].boss1_hp
        current_day = 0
        lasthit_users = []
        ordernum = 0
        if has_manual_hits:
            hits = self.hits.order_by('day', 'order')
        else:
            hits = self.hits.order_by('day', 'ingame_timestamp', 'order')
        hits = list(hits.all())
        for hit in hits:
            if current_day != hit.day:
                current_day = hit.day
                lasthit_users = []
            ordernum += 1
            hit.order = ordernum
            hit.boss_lap = self.current_lap
            hit.boss_number = self.current_boss
            hit.actual_damage = min(hit.damage, self.current_hp)
            if hit.member_id in lasthit_users:
                hit.hit_type = ClanBattleHitType.CARRYOVER
                lasthit_users.remove(hit.member_id)
            elif hit.actual_damage == self.current_hp:
                hit.hit_type = ClanBattleHitType.LAST_HIT
                lasthit_users.append(hit.member_id)
            else:
                hit.hit_type = ClanBattleHitType.NORMAL
            self.current_hp -= hit.actual_damage
            hit.boss_hp_left = self.current_hp
            if hit.has_changed:
                hit.save()
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

    @cached_property
    def in_progress(self):
        if self.start_time is None or self.end_time is None:
            return False
        now = timezone.now()
        return self.start_time <= now and self.end_time > now

    def boss_list(self):
        boss_l = []
        for num in range(1, 6):
            boss_l.append({"icon": getattr(self, 'boss%d_iconid' % num), "name": getattr(self, 'boss%d_name' % num)})
        return boss_l

    @cached_property
    def current_day(self):
        if self.start_time is None or self.end_time is None:
            return 0
        now = timezone.now()
        first_day_reset = self.start_time.replace(hour=13, minute=0, second=0, microsecond=0)
        started_before_reset = self.start_time.hour < 13
        return math.floor((now - first_day_reset).total_seconds() / 86400) + (2 if started_before_reset else 1)

    @cached_property
    def total_days(self):
        if self.start_time is None or self.end_time is None:
            return 0
        first_day_reset = self.start_time.replace(hour=13, minute=0, second=0, microsecond=0)
        started_before_reset = self.start_time.hour < 13
        return math.floor((self.end_time - first_day_reset).total_seconds() / 86400) + (
            2 if started_before_reset else 1)

    @cached_property
    def next_reset(self):
        now = timezone.now()
        if now.hour >= 13:
            now = now + datetime.timedelta(days=1)
        return now.replace(hour=13, minute=0, second=0, microsecond=0)

    def day_of(self, dt):
        if self.start_time is None or self.end_time is None:
            return 0
        first_day_reset = self.start_time.replace(hour=13, minute=0, second=0, microsecond=0)
        started_before_reset = self.start_time.hour < 13
        return max(min(math.floor((dt - first_day_reset).total_seconds() / 86400) + (2 if started_before_reset else 1),
                       self.total_days), 1)

    @property
    def current_boss_icon(self):
        return getattr(self, 'boss%d_iconid' % self.current_boss)

    @property
    def current_boss_name(self):
        return getattr(self, 'boss%d_name' % self.current_boss)

    @cached_property
    def hits_today(self):
        return self.hits_on_day(self.current_day)

    def hits_on_day(self, day):
        with connection.cursor() as cur:
            cur.execute("""
            SELECT COALESCE(SUM(CASE WHEN "hit_type" = 'Normal' THEN 1 ELSE 0.5 END), 0)
            FROM "rong_clanbattlescore"
            WHERE "clan_battle_id" = %s AND "day" = %s
            """, [self.id, day])
            return cur.fetchone()[0]

    @cached_property
    def total_daily_hits(self):
        return self.clan.in_clan_members.count() * ClanBattle.HITS_PER_DAY

    @cached_property
    def hits_left_today(self):
        return self.total_daily_hits - self.hits_today

    def user_hits_today(self, user_id):
        return self.user_hits_on_day(user_id, self.current_day)

    def user_hits_on_day(self, user_id, day):
        with connection.cursor() as cur:
            cur.execute("""
            SELECT COALESCE(SUM(CASE WHEN "hit_type" = 'Normal' THEN 1 ELSE 0.5 END), 0)
            FROM "rong_clanbattlescore" cbs
            JOIN "rong_clanmember" m ON cbs."member_id" = m."id"
            WHERE cbs."clan_battle_id" = %s AND cbs."day" = %s AND m."user_id" = %s
            """, [self.id, day, user_id])
            return cur.fetchone()[0]

    def member_hits_today(self, member_id):
        return self.member_hits_on_day(member_id, self.current_day)

    def member_hits_on_day(self, member_id, day):
        with connection.cursor() as cur:
            cur.execute("""
            SELECT COALESCE(SUM(CASE WHEN "hit_type" = 'Normal' THEN 1 ELSE 0.5 END), 0)
            FROM "rong_clanbattlescore" cbs
            WHERE cbs."clan_battle_id" = %s AND cbs."day" = %s AND cbs."member_id" = %s
            """, [self.id, day, member_id])
            return cur.fetchone()[0]

    @cached_property
    def damage_dealt_today(self):
        return self.damage_dealt_on_day(self.current_day)

    def damage_dealt_on_day(self, day):
        return self.hits.filter(day=day).aggregate(Sum('actual_damage'))["actual_damage__sum"] or 0

    @cached_property
    def bosses_killed_today(self):
        return self.bosses_killed_on_day(self.current_day)

    def bosses_killed_on_day(self, day):
        return self.hits.filter(day=day, boss_hp_left=0).count()

    def user_damage_dealt_today(self, user_id):
        return self.user_damage_dealt_on_day(user_id, self.current_day)

    def user_damage_dealt_on_day(self, user_id, day):
        return self.hits.filter(day=day, member__user_id=user_id).aggregate(Sum('actual_damage'))[
                   "actual_damage__sum"] or 0

    @cached_property
    def ended(self):
        if self.start_time is None:
            return False
        now = timezone.now()
        return self.end_time <= now

    @cached_property
    def day_range(self):
        return range(1, self.total_days + 1)

    def initial_matrix_row(self, member):
        return {
            "member": member,
            "total_damage": 0,
            "total_score": 0,
            "total_ascore": 0,
            "has_groups": False,
            "days": [{
                "hits": 0,
                "damage": 0,
                "score": 0,
                "ascore": 0,
                "hit_damage": [0 for n in range(ClanBattle.HITS_PER_DAY)],
                "hit_score": [0 for n in range(ClanBattle.HITS_PER_DAY)],
                "hit_ascore": [0 for n in range(ClanBattle.HITS_PER_DAY)],
                "hit_group": ["N/A" for n in range(ClanBattle.HITS_PER_DAY)],
            } for n in range(self.total_days)],
            "hits": [],
            "tags": defaultdict(lambda: 0),
            "in_clan": not member.out_of_clan
        }

    def get_boss_info(self, boss_data, difficulty_idx):
        cbi = boss_data[difficulty_idx].boss_list
        return {
            "info": cbi,
            "lap_hp": sum(boss["hp"] for boss in cbi),
        }

    @cached_property
    def hit_data_for_stats(self):
        return list(self.hits.order_by('order').select_related('member', 'member__user', 'pilot', 'pilot__user',
                                                               'group', 'comp').prefetch_related('tags'))

    @cached_property
    def hit_stats(self):
        boss_data = list(self.bosses.order_by('difficulty').all())
        difficulty_idx = 0
        curr_boss_info = self.get_boss_info(boss_data, difficulty_idx)
        hit_matrix = OrderedDict()
        if self.in_progress:
            # if CB in progress, include all active members so 0/3 hit people can be seen
            members = list(self.clan.in_clan_members.select_related('user'))
            members.sort(key=lambda x: x.ign.lower())
            for member in members:
                hit_matrix[member.id] = self.initial_matrix_row(member)
        stats = {
            "daily_damage": [0 for n in range(self.total_days)],
            "cumu_damage": [0 for n in range(self.total_days)],
            "daily_score": [0 for n in range(self.total_days)],
            "cumu_score": [0 for n in range(self.total_days)],
            "daily_ascore": [0 for n in range(self.total_days)],
            "cumu_ascore": [0 for n in range(self.total_days)],
            "daily_laps": [0 for n in range(self.total_days)],
            "cumu_laps": [0 for n in range(self.total_days)],
            "daily_end": [{
                "lap": 1,
                "boss": self.boss1_name,
                "hp": curr_boss_info["info"][0]["hp"],
            } for n in range(self.total_days)],
            "tags": set(),
        }
        weightable_hits = [[0 for n in range(5)] for i in range(len(boss_data))]
        weightable_dmg = [[0 for n in range(5)] for i in range(len(boss_data))]
        weight_ts = 0
        weight_th = 0
        for hit in self.hit_data_for_stats:
            if boss_data[difficulty_idx].lap_to is not None and hit.boss_lap > boss_data[difficulty_idx].lap_to:
                difficulty_idx += 1
                curr_boss_info = self.get_boss_info(boss_data, difficulty_idx)
            if hit.member_id not in hit_matrix:
                hit_matrix[hit.member_id] = self.initial_matrix_row(hit.member)
            if hit.pilot_id and hit.pilot_id not in hit_matrix:
                hit_matrix[hit.pilot_id] = self.initial_matrix_row(hit.pilot)
            entry = hit_matrix[hit.member_id]
            entry["in_clan"] = True
            if int(entry['days'][hit.day - 1]['hits']) >= ClanBattle.HITS_PER_DAY:
                continue  # silently ignore extra hits to avoid kabooming the dashboard
            entry["hits"].append(hit)
            stats["tags"].update(hit.tags.all())
            for tag in hit.tags.all():
                entry["tags"][tag.id] += 1
            hit.difficulty = difficulty_idx
            hit.score = math.ceil(hit.actual_damage * curr_boss_info["info"][hit.boss_number - 1]["multiplier"])
            entry['total_damage'] += hit.actual_damage
            entry['total_score'] += hit.score
            stats["daily_damage"][hit.day - 1] += hit.actual_damage
            stats["daily_score"][hit.day - 1] += hit.score
            stats["daily_laps"][hit.day - 1] += hit.actual_damage / curr_boss_info["lap_hp"]
            entry['days'][hit.day - 1]['damage'] += hit.actual_damage
            entry['days'][hit.day - 1]['score'] += hit.score
            hit.hit_index = int(entry['days'][hit.day - 1]['hits'])
            entry['days'][hit.day - 1]['hit_damage'][hit.hit_index] += hit.actual_damage
            entry['days'][hit.day - 1]['hit_score'][hit.hit_index] += hit.score
            if hit.hit_type == ClanBattleHitType.NORMAL:
                entry['days'][hit.day - 1]['hits'] += 1
            else:
                entry['days'][hit.day - 1]['hits'] += 0.5
            if hit.hit_type != ClanBattleHitType.CARRYOVER and hit.group:
                entry['has_groups'] = True
                entry['days'][hit.day - 1]['hit_group'][hit.hit_index] = hit.group.name
            if hit.hit_type == ClanBattleHitType.NORMAL or (
                    hit.hit_type == ClanBattleHitType.LAST_HIT and hit.damage / hit.actual_damage >= 1.1):
                weightable_hits[hit.difficulty][hit.boss_number - 1] += 1
                weightable_dmg[hit.difficulty][hit.boss_number - 1] += hit.damage
                weight_ts += math.ceil(hit.damage * curr_boss_info["info"][hit.boss_number - 1]["multiplier"])
                weight_th += 1
            for i in range(hit.day - 1, self.total_days):
                stats["daily_end"][i]["lap"] = hit.boss_lap
                stats["daily_end"][i]["boss"] = getattr(self, 'boss%d_name' % hit.boss_number)
                stats["daily_end"][i]["hp"] = hit.boss_hp_left

        stats["tags"] = list(stats["tags"])
        for tag in stats["tags"]:
            tag.total = 0
        for mid in hit_matrix:
            entry = hit_matrix[mid]
            old_tags = entry["tags"]
            entry["tags"] = []
            for tag in stats["tags"]:
                entry["tags"].append(old_tags[tag.id])
                tag.total += old_tags[tag.id]
            for hit in hit_matrix[mid]["hits"]:
                if weightable_hits[hit.difficulty][hit.boss_number - 1]:
                    norm_boss_score = weightable_hits[hit.difficulty][hit.boss_number - 1] / weight_th * weight_ts
                    norm_mult = norm_boss_score / weightable_dmg[hit.difficulty][hit.boss_number - 1]
                    norm_score = math.ceil(hit.actual_damage * norm_mult)
                else:
                    norm_score = hit.score
                entry['total_ascore'] += norm_score
                entry['days'][hit.day - 1]['ascore'] += norm_score
                entry['days'][hit.day - 1]['hit_ascore'][hit.hit_index] += norm_score
                stats["daily_ascore"][hit.day - 1] += norm_score

        # cumu stuff
        for n in range(self.total_days):
            stats["cumu_damage"][n] = sum(stats["daily_damage"][0:n + 1])
            stats["cumu_score"][n] = sum(stats["daily_score"][0:n + 1])
            stats["cumu_ascore"][n] = sum(stats["daily_ascore"][0:n + 1])
            stats["cumu_laps"][n] = sum(stats["daily_laps"][0:n + 1])
        stats["players"] = list(hit_matrix.values())
        return stats

    def get_pilot_stats(self, overtime_as_full):
        def initial_row(member):
            return {
                "member": member,
                "total_own": 0,
                "total_piloted": 0,
                "total_total": 0,
                "days": [{
                    "own": 0,
                    "piloted": 0,
                    "total": 0,
                } for n in range(self.total_days)],
            }

        pilot_matrix = {}
        for hit in self.hit_data_for_stats:
            if hit.member_id not in pilot_matrix:
                pilot_matrix[hit.member_id] = initial_row(hit.member)
            if hit.pilot_id and hit.pilot_id not in pilot_matrix:
                pilot_matrix[hit.pilot_id] = initial_row(hit.pilot)

            value = 0.5 if (not overtime_as_full and not hit.hit_type == ClanBattleHitType.NORMAL) else 1

            if not hit.pilot_id or hit.pilot_id == hit.member_id:
                pilot_matrix[hit.member_id]["total_own"] += value
                pilot_matrix[hit.member_id]["total_total"] += value
                pilot_matrix[hit.member_id]["days"][hit.day - 1]["own"] += value
                pilot_matrix[hit.member_id]["days"][hit.day - 1]["total"] += value
            else:
                pilot_matrix[hit.pilot_id]["total_piloted"] += value
                pilot_matrix[hit.pilot_id]["total_total"] += value
                pilot_matrix[hit.pilot_id]["days"][hit.day - 1]["piloted"] += value
                pilot_matrix[hit.pilot_id]["days"][hit.day - 1]["total"] += value

        aggregate_stats = {
            "total_own": sum(pilot_matrix[k]["total_own"] for k in pilot_matrix),
            "total_piloted": sum(pilot_matrix[k]["total_piloted"] for k in pilot_matrix),
            "total_total": sum(pilot_matrix[k]["total_total"] for k in pilot_matrix),
            "days": [{
                "own": sum(pilot_matrix[k]["days"][n]["own"] for k in pilot_matrix),
                "piloted": sum(pilot_matrix[k]["days"][n]["piloted"] for k in pilot_matrix),
                "total": sum(pilot_matrix[k]["days"][n]["total"] for k in pilot_matrix),
            } for n in range(self.total_days)]
        }

        return {
            "players": list(pilot_matrix.values()),
            "aggregate": aggregate_stats
        }

    @cached_property
    def pilot_stats_clashes(self):
        return self.get_pilot_stats(True)

    @cached_property
    def pilot_stats_hitcount(self):
        return self.get_pilot_stats(False)

    @cached_property
    def comp_stats(self):
        def initial_row(comp):
            return {
                "comp": comp.name,
                "hits": [],
                "mean": 0,
                "median": 0,
                "minimum": 0,
                "maximum": 0,
                "lower_quartile": 0,
                "upper_quartile": 0,
                "player_info": {},
            }

        def initial_player_row(name):
            return {
                "name": name,
                "hits": [],
                "count": 0,
                "mean": 0,
                "median": 0,
                "average_score": 0,
            }

        def find_median(sorted_list):
            indices = []
            list_size = len(sorted_list)
            if list_size % 2 == 0:
                indices.append(int(list_size / 2) - 1)  # -1 because index starts from 0
                indices.append(int(list_size / 2))
                median = (sorted_list[indices[0]] + sorted_list[indices[1]]) / 2
            else:
                indices.append(int(list_size / 2))
                median = sorted_list[indices[0]]
            return median, indices

        boss_data = list(self.bosses.order_by('difficulty').all())
        difficulty_idx = 0
        comp_matrix = {}
        for hit in self.hit_data_for_stats:
            if boss_data[difficulty_idx].lap_to is not None and hit.boss_lap > boss_data[difficulty_idx].lap_to:
                difficulty_idx += 1
            if hit.hit_type == ClanBattleHitType.CARRYOVER or not hit.comp:
                continue
            if hit.hit_type == ClanBattleHitType.LAST_HIT and hit.damage / hit.actual_damage < 1.1:
                continue
            if hit.boss_number != hit.comp.boss_number or difficulty_idx != hit.comp.boss_phase - 1:
                continue
            if hit.comp.id not in comp_matrix:
                comp_matrix[hit.comp.id] = initial_row(hit.comp)
            comp_matrix[hit.comp.id]["hits"].append({
                "player": hit.player_name,
                "damage": hit.damage,
                "lap": hit.boss_lap
            })

        for comp in comp_matrix.values():
            comp["hits"].sort(key=lambda x: -x["damage"])
            hit_count = len(comp["hits"])
            for idx, hit in enumerate(comp["hits"]):
                hit["score"] = 100 if hit_count == 1 else 100 - idx * (100 / (hit_count - 1))
                if hit["player"] not in comp["player_info"]:
                    comp["player_info"][hit["player"]] = initial_player_row(hit["player"])
                comp["player_info"][hit["player"]]["hits"].append(hit)
            damages = sorted(hit["damage"] for hit in comp["hits"])
            comp['mean'] = round(sum(damages) / hit_count)
            median, median_indices = find_median(damages)
            if hit_count == 1:
                Q1 = Q3 = median
            elif hit_count == 2:
                Q1 = damages[0]
                Q3 = damages[1]
            else:
                Q1, Q1_indices = find_median(damages[:median_indices[0]])
                Q3, Q3_indices = find_median(damages[median_indices[-1] + 1:])
            comp['median'] = median
            comp['minimum'] = min(damages)
            comp['maximum'] = max(damages)
            comp['lower_quartile'] = Q1
            comp['upper_quartile'] = Q3

            for player in comp["player_info"].values():
                player["count"] = len(player["hits"])
                player["mean"] = round(sum(hit["damage"] for hit in player["hits"]) / player["count"])
                player["median"] = statistics.median(hit["damage"] for hit in player["hits"])
                player["average_score"] = sum(hit["score"] for hit in player["hits"]) / player["count"]
                del player["hits"]
            comp["player_info"] = list(comp["player_info"].values())
            comp["player_info"].sort(key=lambda x: -x["average_score"])

        comps = list(comp_matrix.values())
        comps.sort(key=lambda x: x["comp"])

        return comps
