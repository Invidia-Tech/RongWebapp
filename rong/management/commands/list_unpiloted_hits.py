from django.core.management.base import BaseCommand
from django.db import connection

from rong.models import ClanBattle, ClanBattleScore, Clan, User, ClanMember, Unit, UnitAlias


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cb_slug')

    def handle(self, *args, **options):
        cb = ClanBattle.objects.filter(slug=options['cb_slug']).first()
        if not cb:
            print("Could not find CB.")
            return
        pilots = {}
        unpiloted = []
        for hit in cb.hits.select_related('member', 'pilot').order_by('order'):
            if hit.pilot_id:
                if hit.pilot.ign not in pilots:
                    pilots[hit.pilot.ign] = 0
                pilots[hit.pilot.ign] += 1
            else:
                if hit.member.ign not in pilots:
                    pilots[hit.member.ign] = 0
                pilots[hit.member.ign] += 1
                # print it
                unpiloted.append("Boss %d - #%03d (Lap %d) - %s attacked for %d damage" % (
                hit.boss_number, hit.order, hit.boss_lap, hit.member.ign, hit.damage))
                pass
        unpiloted.sort()
        for up in unpiloted:
            print(up)
        print(str(pilots))
