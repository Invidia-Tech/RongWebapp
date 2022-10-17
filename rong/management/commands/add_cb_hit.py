from django.core.management.base import BaseCommand

from rong.models import ClanBattle, ClanBattleScore


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cb_name')
        parser.add_argument('day', type=int)
        parser.add_argument('member_name')
        parser.add_argument('damage', type=int)

    def handle(self, *args, **options):
        battle = ClanBattle.objects.get(name=options['cb_name'])
        member = battle.clan.members.get(ign__iexact=options['member_name'])
        if battle.user_hits_on_day(member.user_id, options['day']) >= 3:
            raise ValueError("Already recorded 3 hits for user+day combo!")
        hit = ClanBattleScore(clan_battle=battle, user=member.user, day=options['day'], damage=options['damage'],
                              ign=member.ign)
        hit.save()
        print("Hit by %s for %d (%d) damage added. Boss status is Lap %d %s, %d HP left" % (
            member.ign, hit.damage, hit.actual_damage, battle.current_lap, battle.current_boss_name, battle.current_hp))
