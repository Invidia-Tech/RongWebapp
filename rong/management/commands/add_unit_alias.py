from django.core.management.base import BaseCommand
from django.db import connection

from rong.models import ClanBattle, ClanBattleScore, Clan, User, ClanMember, Unit, UnitAlias


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('unit_name_or_id')
        parser.add_argument('alias')

    def handle(self, *args, **options):
        unit = Unit.objects.filter(name__iexact=options['unit_name_or_id']).first()
        if not unit:
            unit = Unit.objects.get(id=options['unit_name_or_id'])
        with connection.cursor() as cur:
            cur.execute('INSERT INTO "rongbot"."unit_alias" ("unit_id", "unit_name") VALUES(%s, %s)', (unit.id, options['alias']))
        print("Successfully added alias %s for unit %s [%d]" % (options['alias'], unit.name, unit.id))
