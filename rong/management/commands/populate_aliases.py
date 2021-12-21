from django.core.management.base import BaseCommand
from django.db import connection

from rong.models import ClanBattle, ClanBattleScore, Clan, User, ClanMember, Unit, UnitAlias


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('data/aliases.txt', 'r', encoding='utf-8') as fh:
            aliases = fh.readlines()

        for aliasline in aliases:
            ln = aliasline.strip()
            if ln:
                unit_id, alias = ln.split(",", 1)
                alias = alias.strip()
                unit = Unit.objects.get(id=int(unit_id))
                if not UnitAlias.objects.filter(name__iexact=alias).exists():
                    with connection.cursor() as cur:
                        cur.execute('INSERT INTO "rongbot"."unit_alias" ("unit_id", "unit_name") VALUES(%s, %s)',
                                    (unit.id, alias))
        print("Done with aliases.")
