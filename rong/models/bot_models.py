from django.db import models

class DiscordRoleMember(models.Model):
    server_id = models.CharField(max_length=30)
    role_id = models.CharField(max_length=30)
    member_id = models.CharField(max_length=30)

    class Meta():
        managed = False
        db_table = u'rongbot"."discord_role_members'

class DiscordServerRoles(models.Model):
    server_id = models.CharField(max_length=30)
    role_id = models.CharField(max_length=30)
    role_name = models.TextField()

    class Meta():
        managed = False
        db_table = u'rongbot"."discord_server_roles'
