from django.core.management.base import BaseCommand

from rong.models import ClanBattle, ClanBattleScore, Clan, User, ClanMember, Unit, UnitAlias


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('unit_name_or_id')
        parser.add_argument('alias')

    def handle(self, *args, **options):
        unit = Unit.objects.filter(name__iexact=options['unit_name_or_id']).first()
        if not unit:
            unit = Unit.objects.get(id=options['unit_name_or_id'])
        UnitAlias(unit_id=unit.id, name=options['alias']).save()
        print("Successfully added alias %s for unit %s [%d]" % (options['alias'], unit.name, unit.id))
