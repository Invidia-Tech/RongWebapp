from django.core.management.base import BaseCommand
from django.db import connection

from rong.models import ClanBattle, ClanBattleScore, Clan, User, ClanMember, Unit, UnitAlias


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cb_slug_or_id')

    def handle(self, *args, **options):
        battle = ClanBattle.objects.filter(slug__iexact=options['cb_slug_or_id']).first()
        if not battle:
            battle = ClanBattle.objects.get(id=options['cb_slug_or_id'])

        # reload with relations
        battle = ClanBattle.objects.filter(id=battle.id).prefetch_related('flights', 'flights__pilot', 'flights__pilot__user').first()
        stats = {}
        for flight in battle.flights.all():
            if flight.pilot_id not in stats:
                stats[flight.pilot_id] = {"name": flight.pilot.user.name, "landed": 0, "amb": 0, "canceled": 0, "crashed": 0, "in flight": 0, "total": 0, "total_complete": 0}
            stats[flight.pilot_id][flight.status] += 1
            stats[flight.pilot_id]["total"] += 1
            if flight.status != "canceled" and flight.status != "in flight":
                stats[flight.pilot_id]["total_complete"] += 1
        for pilot in stats:
            print(str(stats[pilot]))

