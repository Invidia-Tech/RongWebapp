from django.db import models


class DiscordRoleMember(models.Model):
    server_id = models.CharField(max_length=30, primary_key=True)  # hack
    role_id = models.CharField(max_length=30)
    member_id = models.CharField(max_length=30)

    class Meta():
        managed = False
        db_table = u'rongbot"."discord_role_members'


class DiscordServerRoles(models.Model):
    server_id = models.CharField(max_length=30, primary_key=True)  # hack
    role_id = models.CharField(max_length=30)
    role_name = models.TextField()

    class Meta():
        managed = False
        db_table = u'rongbot"."discord_server_roles'


class UnitAlias(models.Model):
    unit_id = models.IntegerField(primary_key=True)  # hack
    name = models.TextField(db_column='unit_name')

    class Meta():
        managed = False
        db_table = u'rongbot"."unit_alias'
