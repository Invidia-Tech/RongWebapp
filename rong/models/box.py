from typing import OrderedDict
from django.db import models
from .redive_models import Unit


class Box(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def missing_units(self):
        all_unit_ids = Unit.valid_units().values_list('id', flat=True)
        current_unit_ids = self.boxunit_set.values_list('unit_id', flat=True)
        return Unit.objects.filter(id__in=(set(all_unit_ids) - set(current_unit_ids)))

    def clan_name(self):
        return self.clanmember.clan.name if hasattr(self, "clanmember") else "None"

    def unit_json(self):
        # use a consistent order for NOW
        # can be removed if wanted after sorts implemented on frontend
        units = OrderedDict()
        for unit in self.boxunit_set.all().select_related('unit').order_by('pk'):
            units[unit.id] = unit.edit_json()
        return units

    def meta_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "clan": self.clan_name(),
            "units": self.unit_json()
        }
