from collections import OrderedDict

from django.db import models
from django.utils.functional import cached_property

from .box_item import BoxItem
from .redive_models import Unit


class Box(models.Model):
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50, null=True)

    def missing_units(self):
        all_unit_ids = Unit.valid_units().values_list('id', flat=True)
        current_unit_ids = self.boxunit_set.values_list('unit_id', flat=True)
        return Unit.objects.filter(id__in=(set(all_unit_ids) - set(current_unit_ids)))

    @cached_property
    def display_name(self):
        if hasattr(self, "clanmember"):
            return "%s - %s" % (self.clanmember.clan.name, self.clanmember.ign)
        else:
            return self.name

    def unit_json(self):
        # use a consistent order for NOW
        # can be removed if wanted after sorts implemented on frontend
        units = OrderedDict()
        ordered_units = list(self.boxunit_set.all())
        ordered_units.sort(key=lambda x: x.id)
        for unit in self.boxunit_set.all():
            units[unit.id] = unit.edit_json()
        return units

    def can_edit(self, user):
        if self.user_id == user.id:
            return True
        if not hasattr(self, "clanmember"):
            return False
        if self.clanmember.user_id == user.id:
            return True
        if self.clanmember.clan_id in user.managed_clan_ids:
            return True
        return False

    def meta_json(self):
        units = self.unit_json()
        return {
            "id": self.id,
            "name": self.display_name,
            "units": units,
            "is_clan": hasattr(self, "clanmember")
        }

    def get_item_quantity(self, item):
        stock = [i for i in self.inventory.all() if i.item == item]
        if not stock:
            return 0
        return stock[0].quantity

    def set_item_quantity(self, item, quantity):
        stock = self.inventory.filter(item=item).first()
        if not stock:
            stock = BoxItem(box=self, item=item)
        stock.quantity = quantity
        stock.save()

    @staticmethod
    def full_data_queryset():
        return Box.objects.select_related("clanmember", "clanmember__clan").prefetch_related(
            'boxunit_set__unit__ranks', 'boxunit_set__unit__unlock_condition', 'boxunit_set__unit__unique_equip',
            'inventory')
