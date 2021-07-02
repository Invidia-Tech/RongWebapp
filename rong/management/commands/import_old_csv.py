import csv
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from rong.models import ClanBattle, ClanMember, ClanBattleScore

def apply_hit(battle, hit_data, day):
    hit = ClanBattleScore(clan_battle=battle, user=hit_data['member'].user, day=day + 1, damage=hit_data['damage'],
                          ign=hit_data['member'].ign)
    hit.save()
    print("Hit by %s for %d (%d) damage added. Boss status is Lap %d %s, %d HP left" % (
        hit.ign, hit.damage, hit.actual_damage, battle.current_lap, battle.current_boss_name, battle.current_hp))


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cb_name')
        parser.add_argument('csv')

    def handle(self, *args, **options):
        battle = ClanBattle.objects.get(name=options['cb_name'])
        with open(options['csv'], newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            rows = [row for row in csvreader]

        # check format
        day_attack_columns = [8, 13, 19, 25, 31] # CB2/3
        member_row_start = 2
        member_row_end = 32
        name_column = 1
        errors = []
        hit_regex = re.compile(r'(?P<damage>[0-9]+)\s*\((?P<lap>[1-9][0-9]*)-(?P<boss>[1-9][0-9]*)(?:[,\/](?P<second_lap>[1-9][0-9]*)(?:-(?P<second_boss>[1-9][0-9]*))?)?\)')
        day_hits = [[] for n in range(5)]

        for row in rows[member_row_start:member_row_end]:
            name = row[name_column]
            member = battle.clan.members.filter(ign__iexact=name).first()
            if not member:
                errors.append("Member %s not found." % name)
            for day, col in enumerate(day_attack_columns):
                for attack in range(3):
                    datapoint = row[col + attack].strip()
                    matched = hit_regex.match(datapoint)
                    if matched:
                        result = matched.groupdict()
                        hit_data = {x:(int(result[x]) if result[x] is not None else None) for x in result}
                        if hit_data['second_lap'] and not hit_data['second_boss']:
                            hit_data['second_boss'] = hit_data['second_lap']
                            hit_data['second_lap'] = hit_data['lap']
                        if hit_data['second_lap'] and (hit_data['second_lap'] < hit_data['lap'] or (hit_data['lap'] == hit_data['second_lap'] and hit_data['boss'] > hit_data['second_boss'])):
                            errors.append("%s's %d hit on day %d value was %s which has invalid carryover" % (
                                name, attack + 1, day + 1, datapoint
                            ))
                        hit_data['member'] = member
                        day_hits[day].append(hit_data)
                    elif datapoint:
                        # if it's any other non-blank string, consider it an error
                        errors.append("%s's %d hit on day %d value was %s which i don't understand" % (
                            name, attack + 1, day + 1, datapoint
                        ))

        if not errors:
            print("No errors, continue to entering")

            with transaction.atomic():
                battle.hits.all().delete()
                battle.recalculate()
                for day in range(5):
                    current_hits = day_hits[day]
                    waiting_hits = []
                    while current_hits:
                        normal_hits = [hit for hit in current_hits if (hit['lap'] == battle.current_lap and hit['boss'] == battle.current_boss and hit['second_lap'] is None)]
                        if normal_hits:
                            for hit_data in normal_hits:
                                apply_hit(battle, hit_data, day)
                            current_hits = [x for x in current_hits if x not in normal_hits]
                        else:
                            killing_hit = [hit for hit in current_hits if (hit['lap'] == battle.current_lap and hit['boss'] == battle.current_boss)]
                            if not killing_hit:
                                raise ValueError("No killing hit found for lap %d, boss %d" % (battle.current_lap, battle.current_boss))
                            if len(killing_hit) > 1:
                                raise ValueError("Multiple killing hits found for lap %d, boss %d" % (battle.current_lap, battle.current_boss))
                            khit_data = killing_hit[0]
                            if khit_data['damage'] < battle.current_hp:
                                raise ValueError("Killing hit for lap %d boss %d not doing enough damage (%d < %d)" % (battle.current_lap, battle.current_boss, khit_data['damage'], battle.current_hp))
                            kh_data = {'member': khit_data['member'], 'damage': battle.current_hp}
                            apply_hit(battle, kh_data, day)
                            waiting_hits.append({'member': khit_data['member'], 'damage': khit_data['damage'] - kh_data['damage'], 'lap': khit_data['second_lap'], 'boss': khit_data['second_boss']})

                            wh_apply = [hit for hit in waiting_hits if (hit['lap'] == battle.current_lap and hit['boss'] == battle.current_boss)]
                            for hit_data in wh_apply:
                                apply_hit(battle, hit_data, day)
                            waiting_hits = [x for x in waiting_hits if x not in wh_apply]
                            current_hits.remove(khit_data)
                    if waiting_hits:
                        raise ValueError("Trailing hit left at end of day")


        else:
            print("The following errors were encountered in the CSV:")
            print(errors)
