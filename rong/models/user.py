from typing import Union

from django.conf import settings
from django.db import connection, models
from django.utils.functional import cached_property
from django.utils.html import format_html
from requests_oauthlib import OAuth2Session

from .bot_models import DiscordRoleMember
from .clan import Clan
from .clan_battle import ClanBattle
from .clan_battle_score import ClanBattleScore
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
        current_membership_roles = {
            membership.clan.platform_id: membership for membership in self.all_clan_memberships.select_related('clan')}
        # add missing clanmembers
        for role in roles_member_of:
            if role not in current_membership_roles:
                membership = ClanMember(user=self, clan=all_clans[role])
                membership.save()
            elif not current_membership_roles[role].active:
                current_membership_roles[role].active = True
                current_membership_roles[role].save()
        # remove incorrect clanmembers
        self.clan_memberships.exclude(
            clan__platform_id__in=roles_member_of).update(active=False, box=None, is_lead=False, group_num=None)

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

    def preload_perms(self):
        self.clan_ids = self.clan_memberships.values_list('clan_id', flat=True)
        self.cbs_with_scores = set(ClanBattleScore.objects.filter(user=self).values_list('clan_battle_id', flat=True))

    def in_clan(self, clan):
        if hasattr(self, 'clan_ids'):
            return clan.id in self.clan_ids
        return self.clan_memberships.filter(clan_id=clan.id).exists()

    def participated_in(self, battle):
        if hasattr(self, 'cbs_with_scores'):
            return battle.id in self.cbs_with_scores
        return battle.hits.filter(user=self).exists()

    @property
    def is_authenticated(self):
        return True

    @property
    def discordname(self):
        return format_html('{}<span class="discriminator">#{}</span>', self.name, '%04d' % self.discriminator)

    @property
    def plaindiscordname(self):
        return "%s#%04d" % (self.name, self.discriminator)

    @property
    def clan_memberships(self):
        return self.all_clan_memberships.filter(active=True)

    @property
    def detailed_boxes(self):
        return self.box_set.select_related("clanmember", "clanmember__clan").prefetch_related(
            'boxunit_set__unit__ranks')


class AnonymousUser:
    is_authenticated = False
