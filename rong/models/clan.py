from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django_extensions.db.fields import AutoSlugField


class Clan(models.Model):
    name = models.CharField(max_length=50)
    platform_id = models.CharField(max_length=30, db_index=True)
    admin = models.ForeignKey(
        'User', null=True, on_delete=models.SET_NULL, related_name='clans_administrated')
    slug = AutoSlugField(populate_from='name', unique=True)
    box_summary_public = models.BooleanField(default=False)

    def get_clan_id(self):
        return self.id

    @cached_property
    def current_cb(self):
        return self.clanbattle_set.exclude(start_time=None).filter(end_time__gt=timezone.now()).order_by(
            'start_time').first()

    @cached_property
    def future_cbs(self):
        near_future_cbs = self.clanbattle_set.exclude(start_time=None).filter(end_time__gt=timezone.now()).order_by(
            'start_time')[1:]
        undated_cbs = self.clanbattle_set.filter(start_time=None).order_by('order')
        return list(near_future_cbs) + list(undated_cbs)

    @cached_property
    def past_cbs(self):
        return self.clanbattle_set.exclude(start_time=None).filter(end_time__lte=timezone.now()).order_by('-start_time')

    def can_be_viewed_by(self, user):
        return self.id in user.managed_clan_ids or user.in_clan(self)

    @property
    def members(self):
        return self.all_members.filter(active=True)
