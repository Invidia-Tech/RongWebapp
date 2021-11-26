from django.core.management.base import BaseCommand, CommandError

from rong.models import Clan, DiscordServerRole, DiscordMember, User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('admin_id', help='Discord user ID for the clan owner')

    def handle(self, *args, **options):
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
        clan = Clan(name=options['name'], admin=user)
        clan.save()
        print("Successfully created clan %s with admin %s#%04d" % (clan.name, user.name, user.discriminator))
