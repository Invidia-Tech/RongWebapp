from typing import Union

from django.conf import settings
from django.db import connection, models
from django.utils.functional import cached_property
from django.utils.html import format_html
from requests_oauthlib import OAuth2Session

from .bot_models import DiscordRoleMember
from .clan import Clan
from .clan_battle import ClanBattle
from .clan_member import ClanMember


class User(models.Model):
    platform_id = models.CharField(max_length=30, db_index=True)
    discriminator = models.IntegerField()
    name = models.CharField(max_length=50)
    display_pic = models.CharField(max_length=6, default='105811')
    single_mode = models.BooleanField(default=True)
    clans = models.ManyToManyField('Clan', through='ClanMember')
    is_superadmin = models.BooleanField(default=False)

    def check_single_mode(self):
        if not self.single_mode:
            return

        num_clans = self.clan_memberships.count()
        num_boxes = self.box_set.count()

        if num_clans > 1 or num_boxes > 1:
            self.single_mode = False
            self.save()
            return

        if not num_boxes:
            box = self.box_set.create(name='My Box')
        else:
            box = self.box_set.get()

        if num_clans:
            clanmemb = self.clan_memberships.get()
            clanmemb.box = box
            clanmemb.save()

    def sync_clans(self):
        all_clans = {clan.platform_id: clan for clan in Clan.objects.all()}
        roles_member_of = [rolemember.role_id for rolemember in DiscordRoleMember.objects.filter(
            member_id=self.platform_id, role_id__in=all_clans.keys())]
        current_membership_roles = [
            membership.clan.platform_id for membership in self.clan_memberships.select_related('clan')]
        # add missing clanmembers
        for role in roles_member_of:
            if role not in current_membership_roles:
                membership = ClanMember(user=self, clan=all_clans[role])
                membership.save()
        # remove incorrect clanmembers
        self.clan_memberships.exclude(
            clan__platform_id__in=roles_member_of).delete()

    def for_discord_session(session: OAuth2Session):
        r = session.get('%s/users/@me' % settings.DISCORD_BASE_URL)
        user_data = r.json()
        user = User.objects.filter(platform_id=user_data['id']).first()
        if not user:
            user = User(platform_id=user_data['id'])
        user.name = user_data['username']
        user.discriminator = user_data['discriminator']
        user.save()
        user.sync_clans()
        return user

    @cached_property
    def managed_clan_ids(self):
        if self.is_superadmin:
            return Clan.objects.values_list('id', flat=True)
        with connection.cursor() as cur:
            cur.execute("""
SELECT cl."id"
FROM "rong_clan" cl
LEFT JOIN "rong_clanmember" cm ON (cl."id" = cm."clan_id" AND cm."user_id" = %s)
WHERE (
	(cm."id" IS NOT NULL AND cm."is_lead" IS TRUE)
	OR cl."admin_id" = %s
);
            """, [self.id] * 2)
            return [row[0] for row in cur.fetchall()]

    @cached_property
    def managed_clans(self):
        return Clan.objects.filter(id__in=self.managed_clan_ids)

    def can_administrate(self, clan: Clan):
        return self.is_superadmin or clan.admin_id == self.id

    def can_manage(self, entity: Union[Clan, ClanBattle]):
        return entity.get_clan_id() in self.managed_clan_ids

    def can_view(self, entity: Union[Clan, ClanBattle]):
        return entity.can_be_viewed_by(self)

    def in_clan(self, clan):
        return self.clan_memberships.filter(clan_id=clan.id).exists()

    @property
    def is_authenticated(self):
        return True

    @property
    def discordname(self):
        return format_html('{}<span class="discriminator">#{}</span>', self.name, '%04d' % self.discriminator)

    @property
    def plaindiscordname(self):
        return "%s#%04d" % (self.name, self.discriminator)


class AnonymousUser:
    is_authenticated = False
