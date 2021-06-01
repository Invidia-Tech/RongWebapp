from rong.models.clan_battle import ClanBattle
from django.db import connection, models
from requests_oauthlib import OAuth2Session
from django.conf import settings
from .box import Box
from .clan import Clan
from .bot_models import DiscordRoleMember
from .clan_member import ClanMember


class User(models.Model):
    platform_id = models.CharField(max_length=30, db_index=True)
    name = models.CharField(max_length=50)
    clans = models.ManyToManyField('Clan', through='ClanMember')
    display_pic = models.CharField(max_length=6, default='105811')
    single_mode = models.BooleanField(default=True)

    def check_single_mode(self):
        if not self.single_mode:
            return

        num_clans = self.clans.count()
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
            clanmemb = ClanMember.objects.get(user=self)
            clanmemb.box = box
            clanmemb.save()

    def sync_clans(self):
        all_clans = {clan.platform_id: clan for clan in Clan.objects.all()}
        roles_member_of = [rolemember.role_id for rolemember in DiscordRoleMember.objects.filter(
            member_id=self.platform_id, role_id__in=all_clans.keys())]
        current_membership_roles = [
            membership.platform_id for membership in self.clans.all()]
        # add missing clanmembers
        for role in roles_member_of:
            if role not in current_membership_roles:
                membership = ClanMember(
                    user=self, clan=all_clans[role], is_lead=False)
                membership.save()
        # remove incorrect clanmembers
        self.clanmember_set.exclude(
            clan__platform_id__in=roles_member_of).delete()

    def for_discord_session(session: OAuth2Session):
        r = session.get('%s/users/@me' % settings.DISCORD_BASE_URL)
        user_data = r.json()
        user, created = User.objects.get_or_create(
            platform_id=user_data['id'], defaults={'name': user_data['username']})
        if user.name != user_data['username']:
            user.name = user_data['username']
            user.save()
        user.sync_clans()
        return user

    def load_managed_clans(self):
        if not hasattr(self, 'managed_clan_ids'):
            with connection.cursor() as cur:
                cur.execute("""
SELECT cl."id"
FROM "rong_clan" cl
JOIN "rong_clancollection" cc ON cl."collection_id" = cc."id"
LEFT JOIN "rong_clanmember" cm ON (cl."id" = cm."clan_id" AND cm."user_id" = %s)
WHERE (
	(cm."id" IS NOT NULL AND cm."is_lead" IS TRUE)
	OR cl."admin_id" = %s
	OR cc."owner_id" = %s
);
                """, [self.id] * 3)
                self.managed_clan_ids = [row[0] for row in cur.fetchall()]

    @property
    def managed_clans(self):
        self.load_managed_clans()
        return Clan.objects.filter(id__in=self.managed_clan_ids)

    def can_manage(self, clan: Clan):
        self.load_managed_clans()
        return clan.id in self.managed_clan_ids
    
    def can_view(self, clan_battle : ClanBattle):
        self.load_managed_clans()
        return clan_battle.clan_id in self.managed_clan_ids or self.clanmember_set.filter(clan_id=clan_battle.clan_id).exists()

    @property
    def is_authenticated(self):
        return True


class AnonymousUser:
    is_authenticated = False
