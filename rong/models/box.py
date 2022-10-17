from collections import OrderedDict

from django.contrib.humanize.templatetags import humanize
from django.db import models
from django.utils import timezone, dateformat
from django.utils.functional import cached_property

from .box_unit import BoxUnit
from .box_item import BoxItem
from .redive_models import Unit, Item, StoryDetail


class Box(models.Model):
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50, null=True)
    last_update = models.DateTimeField(null=True)

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

    def as_json(self, include_units=True):
        units = self.unit_json() if include_units else {}
        return {
            "id": self.id,
            "name": self.display_name,
            "units": units,
            "is_clan": hasattr(self, "clanmember"),
            "last_update": "N/A" if not self.last_update else humanize.naturaltime(self.last_update),
            "last_update_unixtime": 0 if not self.last_update else dateformat.format(self.last_update, 'U')
        }

    def setup_inventory_cache(self):
        if not hasattr(self, '_inventory_cache'):
            self._inventory_cache = {stock.item: stock for stock in self.inventory.all()}

    def get_item_quantity(self, item):
        self.setup_inventory_cache()
        if item not in self._inventory_cache:
            return 0
        return self._inventory_cache[item].quantity

    def set_item_quantity(self, item, quantity):
        self.setup_inventory_cache()
        if item not in self._inventory_cache:
            self._inventory_cache[item] = BoxItem(box=self, item=item, quantity=0)
        if quantity != self._inventory_cache[item].quantity:
            self._inventory_cache[item].quantity = quantity
            self._inventory_cache[item].save()

    def bulk_update_inventory(self, quantities):
        self.setup_inventory_cache()
        updates = []
        for item in quantities:
            if item not in self._inventory_cache:
                if quantities[item]:
                    self._inventory_cache[item] = BoxItem(box=self, item=item, quantity=quantities[item])
                    self._inventory_cache[item].save()
            elif self._inventory_cache[item].quantity != quantities[item]:
                self._inventory_cache[item].quantity = quantities[item]
                updates.append(self._inventory_cache[item])

        if updates:
            BoxItem.objects.bulk_update(updates, ['quantity'])

    def flag_updated(self):
        self.last_update = timezone.now()
        self.save()

    def inventory_json(self, items=None):
        if items is None:
            items = Item.inventory_items()
        return [{"id": item.id, "name": item.name, "quantity": self.get_item_quantity(item.id), "limit": item.limit_num}
                for item in items]

    def import_loadindex(self, data):
        if "unit_list" not in data and "data" in data:
            data = data["data"]
        if "unit_list" not in data:
            raise ValueError("Did not receive /load/index")
        all_units = {u.id: u for u in Unit.valid_units().prefetch_related('ranks')}
        save_units = []
        new_units = 0
        skill_levels = [
            ["ub_level", "union_burst", 0],
            ["s1_level", "main_skill", 0],
            ["s2_level", "main_skill", 1],
            ["ex_level", "ex_skill", 0],
        ]
        story_loves = {story.id: story.love_level for story in StoryDetail.objects.all()}
        for unit in data["unit_list"]:
            uid = unit["id"]
            if uid in all_units:
                unit_data = all_units[uid]
                box_unit = self.boxunit_set.filter(unit_id=uid).first()
                if not box_unit:
                    box_unit = BoxUnit(box=self, unit_id=uid, level=BoxUnit.max_level())
                    new_units += 1
                if unit["promotion_level"] > unit_data.ranks.count():
                    raise ValueError(
                        "You have %s's rank set to %d ingame, which is beyond current EN ranks." % (
                            unit_data.name, unit["p"]))
                box_unit.rank = unit["promotion_level"]
                box_unit.star = unit["unit_rarity"]
                box_unit.level = unit["unit_level"]
                for eq in range(6):
                    eq_val = unit["equip_slot"][eq]["enhancement_level"] if unit["equip_slot"][eq][
                        "is_slot"] else None
                    setattr(box_unit, 'equip%d' % (eq + 1), eq_val)
                box_unit.ue_level = None
                if unit["unique_equip_slot"] and unit["unique_equip_slot"][0]["is_slot"]:
                    box_unit.ue_level = unit["unique_equip_slot"][0]["enhancement_level"]
                for skill in skill_levels:
                    if len(unit[skill[1]]) > skill[2]:
                        setattr(box_unit, skill[0], unit[skill[1]][skill[2]]["skill_level"])
                    else:
                        setattr(box_unit, skill[0], None)
                read_bonds = [n for n in data["read_story_ids"] if n // 1000 == uid // 100]
                if read_bonds:
                    max_bond = story_loves[max(read_bonds)]
                    box_unit.bond = max_bond if max_bond else 1
                else:
                    box_unit.bond = 1
                box_unit.power = unit["power"]
                save_units.append(box_unit)
            else:
                raise ValueError("Missing unit found in your import.")

        for box_unit in save_units:
            box_unit.save()

        self.boxunit_set.exclude(id__in=[bu.id for bu in save_units]).delete()
        item_ids = [item.id for item in Item.inventory_items()]
        quantities = {item_id: 0 for item_id in item_ids}
        for item in data["item_list"]:
            if item["id"] in item_ids:
                quantities[item["id"]] = item["stock"]
        for item_id in item_ids:
            if item_id not in quantities:
                quantities[item_id] = 0
        self.bulk_update_inventory(quantities)
        self.flag_updated()

        return len(save_units), new_units

    @staticmethod
    def full_data_queryset():
        return Box.objects.select_related("clanmember", "clanmember__clan").prefetch_related(
            'boxunit_set__unit__ranks', 'boxunit_set__unit__unique_equip', 'boxunit_set__unit__rarity_6_quest',
            'inventory')
