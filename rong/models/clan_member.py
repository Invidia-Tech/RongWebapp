from django.apps import apps
from django.contrib.humanize.templatetags import humanize
from django.db import models

from .box import Box


class ClanMember(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='all_clan_memberships', null=True)
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE, related_name='all_members')
    ign = models.CharField(max_length=20)
    player_id = models.PositiveIntegerField(null=True)
    is_lead = models.BooleanField(default=False)
    group_num = models.PositiveIntegerField(null=True)
    box = models.OneToOneField('Box', null=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=True)

    @property
    def formatted_id(self):
        if not self.player_id:
            return "N/A"
        str_id = "%09d" % self.player_id
        return str_id[0:3] + " " + str_id[3:6] + " " + str_id[6:9]

    @property
    def json(self):
        return self.as_json(include_units=False)

    def as_json(self, include_units):
        return {
            "id": self.id,
            "ign": self.ign,
            "player_id": self.player_id,
            "is_lead": self.is_lead,
            "group_num": self.group_num,
            "is_admin": self.user_id == self.clan.admin_id,
            "is_superadmin": False if not self.user_id else self.user.is_superadmin,
            "discord_id": None if not self.user_id else self.user.platform_id,
            "discord_username": None if not self.user_id else self.user.name,
            "discord_discriminator": None if not self.user_id else self.user.discriminator,
            "active": self.active,
            "box": self.box.as_json(include_units=include_units),
        }

    @property
    def user_display_name(self):
        if self.user_id:
            return "%s (%s#%04d)" % (self.ign, self.user.name, self.user.discriminator)
        else:
            return self.ign

    def save(self, *args, **kwargs):
        if not self.box:
            self.box = Box()
            self.box.save()
        if not self.active:
            self.is_lead = False
        super(ClanMember, self).save(*args, **kwargs)
