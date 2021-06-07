from django.core.management.base import BaseCommand, CommandError

from rong.models import ClanCollection, DiscordMember, User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('server_id', help='Discord server ID for the clan group')
        parser.add_argument('owner_id', help='Discord user ID for the collection owner')

    def handle(self, *args, **options):
        if ClanCollection.objects.filter(platform_id=options['server_id']).exists():
            raise CommandError("Clan collection for given server already exists")
        dm_info = DiscordMember.objects.filter(member_id=options['owner_id']).first()
        if not dm_info:
            raise CommandError("I don't know that member, please get the bot into their server first")
        # create shell account if needed
        user = User.objects.filter(platform_id=options['owner_id']).first()
        if not user:
            user = User(platform_id=dm_info.member_id, name=dm_info.username,
                     discriminator=dm_info.discriminator)
            user.save()
        # create clancollection
        cc = ClanCollection(name=options['name'], owner=user, platform_id=options['server_id'])
        cc.save()

        print("Successfully created clan collection %s with owner %s#%04d" % (cc.name, user.name, user.discriminator))
