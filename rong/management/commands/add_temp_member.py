from django.core.management.base import BaseCommand

from rong.models import ClanBattle, ClanBattleScore, Clan, User, ClanMember


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('clan_name')
        parser.add_argument('member_info')
        # parser.add_argument('ign')
        # parser.add_argument('discord_name')
        # parser.add_argument('discriminator')
        # parser.add_argument('discord_id')

    def handle(self, *args, **options):
        clan = Clan.objects.get(name=options['clan_name'])

        mi = options['member_info']
        options['ign'] = mi[:mi.index(":")]
        options['discord_name'] = mi[mi.index(":")+1:mi.index("#")].strip()
        options['discriminator'] = mi[mi.index("#")+1:mi.index("#")+5]
        options['discord_id'] = mi[mi.rindex(" ")+1:].strip()

        user = User.objects.filter(platform_id=options['discord_id']).first()
        if not user:
            user = User(platform_id=options['discord_id'], discriminator=int(options['discriminator']), name=options['discord_name'])
            user.save()

        membership = ClanMember.objects.filter(clan=clan, user=user).first()
        if not membership:
            membership = ClanMember(clan=clan, user=user)
        membership.ign = options['ign']
        membership.save()

        print("Successfully created temp member data for %s." % options['ign'])
