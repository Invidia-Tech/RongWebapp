from django.db import models


class ClanMember(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='clan_memberships')
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE, related_name='members')
    ign = models.CharField(max_length=20, null=True)
    player_id = models.PositiveIntegerField(null=True)
    is_lead = models.BooleanField(default=False)
    group_num = models.PositiveIntegerField(null=True)
    box = models.OneToOneField('Box', null=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return self.clan.name

    @property
    def formatted_id(self):
        if not self.player_id:
            return "N/A"
        str_id = "%09d" % self.player_id
        return str_id[0:3] + " " + str_id[3:6] + " " + str_id[6:9]

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.user.name,
            "discriminator": self.user.discriminator,
            "ign": self.ign,
            "player_id": self.player_id,
            "is_lead": self.is_lead,
            "group_num": self.group_num,
            "is_owner": self.user_id == self.clan.collection.owner_id,
            "is_admin": self.user_id == self.clan.admin_id
        }

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'clan'], name='unique user clan')
        ]
