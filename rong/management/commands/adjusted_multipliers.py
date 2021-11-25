import json
import math

from django.core.management.base import BaseCommand
from django.forms import model_to_dict

from rong.models import Equipment, ClanBattle
from rong.models.clan_battle_score import ClanBattleHitType


class Command(BaseCommand):

    def handle(self, *args, **options):
        multipliers = [[1.3915,1.4850,1.7855,1.5115,1.5540,1.7895],[1.5337,1.4885,1.9660,1.6598,1.7965,2.1285],[2.1270,2.2233,2.1062,2.0450,1.9283,3.0799]]
        cb = ClanBattle.objects.get(slug='ethereal-cb10-capricorn')
        boss_data = list(cb.bosses.order_by('difficulty').all())
        difficulty_idx = 0
        hits = list(cb.hits.order_by('order').select_related('user', 'team'))
        scores = {}

        for hit in hits:
            if boss_data[difficulty_idx].lap_to is not None and hit.boss_lap > boss_data[difficulty_idx].lap_to:
                difficulty_idx += 1
            team_units = [hit.team.unit1_id, hit.team.unit2_id, hit.team.unit3_id, hit.team.unit4_id, hit.team.unit5_id]
            mult_index = hit.boss_number - 1
            if 107801 not in team_units and (107101 not in team_units or 104301 not in team_units):
                # COPIUM
                mult_index = 5
            if difficulty_idx == 2 and mult_index == 4 and 107801 in team_units and hit.hit_type == ClanBattleHitType.NORMAL:
                # COPIUM
                mult_index = 5
            if hit.ign not in scores:
                scores[hit.ign] = 0
            scores[hit.ign] += hit.actual_damage * multipliers[difficulty_idx][mult_index]
        score_sum = sum(scores[k] for k in scores)
        score_list = [[k, scores[k], scores[k] * 1450083190 / score_sum] for k in scores]
        score_list.sort(key=lambda v: -v[1])
        for item in score_list:
            print("%s: %d / %d" % (item[0], math.ceil(item[1]), math.ceil(item[2])))
        print(sum(v[1] for v in score_list))


