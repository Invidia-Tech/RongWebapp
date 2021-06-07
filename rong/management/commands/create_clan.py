from django.core.management.base import BaseCommand, CommandError

from rong.models import Clan, DiscordServerRole, ClanCollection, DiscordMember, User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('role_id', help='Discord role ID for the clan group')
        parser.add_argument('admin_id', help='Discord user ID for the collection owner')

    def handle(self, *args, **options):
        if Clan.objects.filter(platform_id=options['role_id']).exists():
            raise CommandError("Clan for given role already exists")
        role_info = DiscordServerRole.objects.filter(role_id=options['role_id']).first()
        if not role_info:
            raise CommandError("I don't know that role, please get the bot into its server first")
        cc = ClanCollection.objects.filter(platform_id=role_info.server_id).first()
        if not cc:
            raise CommandError("No clan collection found for that role's server, please create_clancollection first")
        dm_info = DiscordMember.objects.filter(member_id=options['admin_id']).first()
        if not dm_info:
            raise CommandError("I don't know that member, please make sure they're in the server")
        # create shell account if needed
        user = User.objects.filter(platform_id=options['admin_id']).first()
        if not user:
            user = User(platform_id=dm_info.member_id, name=dm_info.username,
                        discriminator=dm_info.discriminator)
            user.save()
        # create clan
        clan = Clan(name=options['name'], collection=cc, admin=user, platform_id=options['role_id'])
        clan.save()
        clan.sync_members()
        print("Successfully created clan %s in collection %s with admin %s#%04d" % (clan.name, cc.name, user.name, user.discriminator))
