from django.apps import apps
from django.db import models
from django.utils.functional import cached_property


class DiscordRoleMember(models.Model):
    server_id = models.CharField(max_length=30, primary_key=True)  # hack
    role_id = models.CharField(max_length=30)
    member = models.ForeignKey('DiscordMember', db_column='member_id', on_delete=models.DO_NOTHING)

    class Meta():
        managed = False
        db_table = u'rongbot"."discord_role_members'


class DiscordServerRole(models.Model):
    server_id = models.CharField(max_length=30, primary_key=True)  # hack
    role_id = models.CharField(max_length=30)
    name = models.TextField()

    class Meta():
        managed = False
        db_table = u'rongbot"."discord_server_roles'


class DiscordMember(models.Model):
    member_id = models.CharField(max_length=30, primary_key=True)
    nickname = models.TextField()
    username = models.TextField()
    discriminator = models.IntegerField()

    class Meta():
        managed = False
        db_table = u'rongbot"."discord_members'


class UnitAlias(models.Model):
    unit_id = models.IntegerField(primary_key=True)  # hack
    name = models.TextField(db_column='unit_name')

    class Meta():
        managed = False
        db_table = u'rongbot"."unit_alias'


class Flight(models.Model):
    call_sign = models.CharField(max_length=20)
    pilot = models.ForeignKey('Pilot', db_column='pilot_id', on_delete=models.DO_NOTHING)
    clan = models.ForeignKey('Clan', db_column='clan_id', on_delete=models.DO_NOTHING, related_name='flights')
    cb = models.ForeignKey('ClanBattle', db_column='cb_id', on_delete=models.DO_NOTHING, related_name='flights')
    passenger = models.ForeignKey('ClanMember', db_column='passenger_id', null=True, on_delete=models.DO_NOTHING)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=20)
    team = models.ForeignKey('Team', db_column='team_id', null=True, on_delete=models.DO_NOTHING)

    class Meta():
        managed = False
        db_table = u'rongbot"."flight'
        ordering = ['id']


class Pilot(models.Model):
    nickname = models.CharField(max_length=40)
    motto = models.TextField()
    code = models.CharField(max_length=10)
    clan = models.ForeignKey('Clan', db_column='clan_id', on_delete=models.DO_NOTHING, related_name='pilots')
    user = models.ForeignKey('User', db_column='user_id', on_delete=models.DO_NOTHING)

    @cached_property
    def clanmember(self):
        cm_model = apps.get_model('rong', 'ClanMember')
        return cm_model.objects.filter(clan_id=self.clan_id, user_id=self.user_id, active=True).first()

    class Meta():
        managed = False
        db_table = u'rongbot"."pilot'
        ordering = ['id']


class ForceQuit(models.Model):
    time = models.TimeField(db_column='time_used', primary_key=True)  # need a single (fake) PK for django
    clanmember = models.ForeignKey('ClanMember', db_column='clanmember_id', on_delete=models.DO_NOTHING,
                                   related_name='forcequits')
    cb = models.ForeignKey('ClanBattle', db_column='cb_id', on_delete=models.DO_NOTHING, related_name='forcequits')
    day = models.IntegerField(db_column='day_used')
    note = models.TextField(null=True)

    class Meta():
        managed = False
        db_table = u'rongbot"."force_quit'
