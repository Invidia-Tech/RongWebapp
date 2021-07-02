import csv
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from rong.models import ClanBattle, ClanMember, ClanBattleScore


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cb_name')
        parser.add_argument('csv')

    def handle(self, *args, **options):
        battle = ClanBattle.objects.get(name=options['cb_name'])
        with open(options['csv'], newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            rows = [row for row in csvreader][1:]

        # check names are present
        names = set(row[2].lower().strip() for row in rows if row[0])
        member_map = {}
        for name in names:
            lookup_name = name
            if lookup_name == 'berrymilk':
                lookup_name = 'KyokaSmile'
            if lookup_name == 'the enemy':
                lookup_name = 'enemy'
            if lookup_name == 'ztneee':
                lookup_name = 'tneee'
            if lookup_name == 'vandral':
                lookup_name = 'vendral'
            member = battle.clan.members.filter(ign__iexact=lookup_name).first()
            if not member:
                raise ValueError("Member %s not found" % lookup_name)
            member_map[name] = member

        with transaction.atomic():
            battle.hits.all().delete()
            battle.recalculate()
            for row in rows:
                if not row[0]:
                    break
                mname = row[2].lower().strip()
                hit = ClanBattleScore(clan_battle=battle, user=member_map[mname].user, ign=member_map[mname].ign, day=int(row[1]), damage=int(row[7].replace(',', '')))
                hit.save()
        print("Done.")

