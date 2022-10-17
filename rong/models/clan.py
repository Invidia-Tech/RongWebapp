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
    def nearest_cb(self):
        now = timezone.now()

        def cb_distance(cb):
            distance_start = now - cb.start_time if now > cb.start_time else cb.start_time - now
            distance_end = now - cb.end_time if now > cb.end_time else cb.end_time - now
            return min(distance_start, distance_end)

        possible_cbs = list(self.clanbattle_set.exclude(start_time=None))
        if not possible_cbs:
            return None
        possible_cbs.sort(key=cb_distance)
        return possible_cbs[0]

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

    @property
    def in_clan_members(self):
        return self.all_members.filter(active=True, out_of_clan=False)
