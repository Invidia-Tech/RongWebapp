from django.db import models
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField

from .bot_models import DiscordRoleMember
from .clan_member import ClanMember

from django.apps import apps


class Clan(models.Model):
    collection = models.ForeignKey('ClanCollection', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    platform_id = models.CharField(max_length=30, db_index=True)
    admin = models.ForeignKey(
        'User', null=True, on_delete=models.SET_NULL, related_name='clans_administrated')
    members = models.ManyToManyField('User', through='ClanMember')
    slug = AutoSlugField(populate_from='name', unique=True)

    def get_clan_id(self):
        return self.id

    def current_cb(self):
        return self.clanbattle_set.filter(end_time__gt=timezone.now()).order_by('start_time').first()

    def future_cbs(self):
        return self.clanbattle_set.filter(end_time__gt=timezone.now()).order_by('start_time')[1:]

    def past_cbs(self):
        return self.clanbattle_set.filter(end_time__lte=timezone.now()).order_by('-start_time')

    def sync_members(self):
        if not self.platform_id:
            return
        intended_members = DiscordRoleMember.objects.filter(role_id=self.platform_id).select_related('member').all()
        member_id_list = [m.member_id for m in intended_members]
        current_intended_members = self.clanmember_set.filter(user__platform_id__in=member_id_list).select_related(
            'user').all()
        current_mem_id_list = [cm.user.platform_id for cm in current_intended_members]
        User = apps.get_model("rong", "User")
        for imember in intended_members:
            if imember.member_id not in current_mem_id_list:
                # find the user, if not found, create a shell account for them
                u = User.objects.filter(platform_id=imember.member_id).first()
                if not u:
                    u = User(platform_id=imember.member_id, name=imember.member.username,
                             discriminator=imember.member.discriminator)
                    u.save()
                # register them as part of the clan, either way
                cm = ClanMember(user=u, clan=self)
                cm.save()
        # delete unwanted members
        self.clanmember_set.exclude(user__platform_id__in=member_id_list).delete()
