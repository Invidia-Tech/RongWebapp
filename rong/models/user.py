from typing import Union

from django.conf import settings
from django.db import connection, models
from django.utils.functional import cached_property
from django.utils.html import format_html
from requests_oauthlib import OAuth2Session

from .bot_models import DiscordMember
from .box import Box
from .clan import Clan
from .clan_battle import ClanBattle
from .clan_battle_score import ClanBattleScore


class User(models.Model):
    platform_id = models.CharField(max_length=30, db_index=True)
    discriminator = models.IntegerField()
    name = models.CharField(max_length=50)
    display_pic = models.CharField(max_length=6, default='105811')
    is_superadmin = models.BooleanField(default=False)

    @staticmethod
    def for_discord_session(session: OAuth2Session):
        r = session.get('%s/users/@me' % settings.DISCORD_BASE_URL)
        user_data = r.json()
        user = User.objects.filter(platform_id=user_data['id']).first()
        if not user:
            user = User(platform_id=user_data['id'])
        user.name = user_data['username']
        user.discriminator = user_data['discriminator']
        user.save()
        return user

    @staticmethod
    def for_discord_id(discord_id):
        memberdata = DiscordMember.objects.filter(member_id=discord_id).first()
        if not memberdata:
            return None
        user = User.objects.filter(platform_id=discord_id).first()
        if not user:
            user = User(platform_id=discord_id)
        user.name = memberdata.username
        user.discriminator = memberdata.discriminator
        user.save()
        return user

    @cached_property
    def clan_associations(self):
        if self.is_superadmin:
            where_part = ""
            args = [self.id]
        else:
            where_part = ' WHERE cm."id" IS NOT NULL OR cl."admin_id" = %s'
            args = [self.id] * 2
        with connection.cursor() as cur:
            cur.execute("""
SELECT cl."id", cl."box_summary_public", cl."admin_id", cm."id", cm."is_lead"
FROM "rong_clan" cl
LEFT JOIN "rong_clanmember" cm ON (cl."id" = cm."clan_id" AND cm."user_id" = %s AND cm."active" is TRUE)""" + where_part + """
ORDER BY (cm."id" IS NOT NULL) DESC, cl."name" ASC;
""", args)
            clan_results = list(cur.fetchall())
        clans = []
        for clan in clan_results:
            manager = self.is_superadmin or clan[2] == self.id or (clan[3] is not None and clan[4])
            clans.append({
                "id": clan[0],
                "is_member": clan[3] is not None,
                "is_manager": manager,
                "boxes_viewable": manager or clan[1]
            })
        return clans

    @cached_property
    def managed_clan_ids(self):
        return [clan["id"] for clan in self.clan_associations if clan["is_manager"]]

    @cached_property
    def listed_clan_ids(self):
        return [clan["id"] for clan in self.clan_associations if clan["boxes_viewable"]]

    @cached_property
    def own_box_ids(self):
        with connection.cursor() as cur:
            cur.execute("""
SELECT box."id"
FROM "rong_box" box
LEFT JOIN "rong_clanmember" cm ON (box."id" = cm."box_id")
WHERE box."user_id" = %s OR (cm."user_id" = %s AND cm."active" IS TRUE)
            """, [self.id] * 2)
            return [row[0] for row in cur.fetchall()]

    @cached_property
    def managed_clans(self):
        return Clan.objects.filter(id__in=self.managed_clan_ids)

    @cached_property
    def listed_clans(self):
        return Clan.objects.filter(id__in=self.listed_clan_ids).order_by("name")

    def can_administrate(self, clan: Clan):
        return self.is_superadmin or clan.admin_id == self.id

    def can_manage(self, entity: Union[Clan, ClanBattle]):
        return entity.get_clan_id() in self.managed_clan_ids

    def can_view(self, entity: Union[Clan, ClanBattle]):
        return entity.can_be_viewed_by(self)

    def can_view_boxes(self, clan: Clan):
        return clan.id in self.listed_clan_ids

    def preload_perms(self):
        self.clan_ids = self.clan_memberships.values_list('clan_id', flat=True)
        self.cbs_with_scores = set(
            ClanBattleScore.objects.filter(member__user=self).values_list('clan_battle_id', flat=True))

    def in_clan(self, clan):
        if hasattr(self, 'clan_ids'):
            return clan.id in self.clan_ids
        return self.clan_memberships.filter(clan_id=clan.id).exists()

    def participated_in(self, battle):
        if hasattr(self, 'cbs_with_scores'):
            return battle.id in self.cbs_with_scores
        return battle.hits.filter(member__user=self).exists()

    @property
    def is_authenticated(self):
        return True

    @property
    def discordname(self):
        return format_html('{}<span class="discriminator">#{}</span>', self.name, '%04d' % self.discriminator)

    @property
    def plaindiscordname(self):
        return "%s#%04d" % (self.name, self.discriminator)

    @cached_property
    def clans(self):
        return Clan.objects.filter(id__in=self.clan_memberships.values_list('clan_id', flat=True))

    @property
    def clan_memberships(self):
        return self.all_clan_memberships.filter(active=True)

    @property
    def boxes(self):
        return Box.full_data_queryset().filter(id__in=self.own_box_ids)


class AnonymousUser:
    is_authenticated = False
