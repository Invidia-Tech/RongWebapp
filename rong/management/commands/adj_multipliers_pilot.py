import json
import math

from django.core.management.base import BaseCommand
from django.forms import model_to_dict

from rong.models import Equipment, ClanBattle
from rong.models.clan_battle_score import ClanBattleHitType


class Command(BaseCommand):

    def handle(self, *args, **options):
        multipliers = [
            [2585/2460,2585/2585,2585/2210,2585/1988,2585/2375,2585/2346,2585/1956],
            [2585/2460,2585/2585,2585/2210,2585/1988,2585/2375,2585/2346,2585/1956],
            [2585/2290,2585/2350,2585/1972,2585/1973,2585/1962,2585/1956,2585/1674.5,2585/1600],
            [2585/1581.5,2585/1850,2585/1700,2585/2064,2585/1570,2585/1722,2585/2064,2585/1400]
        ]
        cb = ClanBattle.objects.get(slug='ethereal-cb11-aquarius')
        boss_data = list(cb.bosses.order_by('difficulty').all())
        difficulty_idx = 0
        hits = list(cb.hits.order_by('order').select_related('member', 'team', 'pilot'))
        scores = {}
        counts = {}

        for hit in hits:
            if hit.hit_type != ClanBattleHitType.NORMAL or hit.actual_damage == 0 or (hit.boss_number==3 and hit.boss_lap==4):
                continue
            if boss_data[difficulty_idx].lap_to is not None and hit.boss_lap > boss_data[difficulty_idx].lap_to:
                difficulty_idx += 1
            team_units = []
            if hit.team is not None:
                team_units = [hit.team.unit1_id, hit.team.unit2_id, hit.team.unit3_id, hit.team.unit4_id, hit.team.unit5_id]
            mult_index = hit.boss_number - 1
            if 107801 not in team_units and (107101 not in team_units or 104301 not in team_units):
                # Physical 3rd
                if difficulty_idx < 2 and mult_index == 1:
                    mult_index = 5 # gryphon phys 3rd
                elif difficulty_idx < 2 and mult_index == 2:
                    mult_index = 6 # beetle phys 3rd
                elif difficulty_idx == 2 and mult_index < 2:
                    mult_index = 5 # phys 3rd goblin/gryphon
                elif difficulty_idx == 2 and mult_index >= 2:
                    mult_index = 7 # phys beetle
                else:
                    raise ValueError("Unknown physical 3rd boss: %d/%d/%d" % (difficulty_idx, mult_index, hit.order))
            if difficulty_idx == 2 and mult_index == 0 and 107801 in team_units:
                # magic gobbo
                mult_index = 5
            if difficulty_idx == 2 and mult_index == 4 and 107801 in team_units:
                # magic aqua2
                mult_index = 6
            if difficulty_idx == 3 and mult_index == 0 and 107101 in team_units and 104301 in team_units:
                # phys gobbo
                mult_index = 5
            if difficulty_idx == 3 and mult_index == 3 and 107101 in team_units and 104301 in team_units:
                # phys snek
                mult_index = 6
            if difficulty_idx == 3 and mult_index == 4 and 107801 in team_units:
                # magic aqua3
                mult_index = 7
            pilot = hit.member if not hit.pilot_id else hit.pilot
            if pilot.ign not in scores:
                scores[pilot.ign] = 0
                counts[pilot.ign] = 0
            scores[pilot.ign] += hit.actual_damage * multipliers[difficulty_idx][mult_index] / 2585000
            counts[pilot.ign] += 1
        score_list = [[k, scores[k] / counts[k]] for k in scores]
        score_list.sort(key=lambda v: -v[1])
        for item in score_list:
            print("%s: %.04f" % (item[0], item[1]))
        print(sum(v[1] for v in score_list))


