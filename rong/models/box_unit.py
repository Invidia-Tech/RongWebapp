import functools

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.forms.models import model_to_dict

from .redive_models import Unit, SkillCost, UniqueEquipmentEnhanceData


def valid_box_unit(value):
    if not Unit.valid_units().filter(id=value).exists():
        raise ValidationError('Unit not in game')


def valid_power(value):
    if value < 100 or value > 100000:
        raise ValidationError('Invalid unit power')


def valid_level(value):
    if value <= 0 or value > BoxUnit.max_level():
        raise ValidationError('Invalid unit level')


promotion_cache = {}


class BoxUnit(models.Model):
    box = models.ForeignKey('Box', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, validators=[valid_box_unit])
    power = models.PositiveIntegerField(null=True, validators=[valid_power])
    level = models.PositiveIntegerField(default=1, validators=[valid_level])
    star = models.PositiveIntegerField(default=1)
    rank = models.PositiveIntegerField(default=1)
    bond = models.PositiveIntegerField(default=1)
    notes = models.TextField(default='', max_length=300)
    # null = unequipped or not specified, 0-5 = refinement stars
    equip1 = models.PositiveIntegerField(null=True)
    equip2 = models.PositiveIntegerField(null=True)
    equip3 = models.PositiveIntegerField(null=True)
    equip4 = models.PositiveIntegerField(null=True)
    equip5 = models.PositiveIntegerField(null=True)
    equip6 = models.PositiveIntegerField(null=True)
    ue_level = models.PositiveIntegerField(null=True)
    ub_level = models.PositiveIntegerField(null=True)
    s1_level = models.PositiveIntegerField(null=True)
    s2_level = models.PositiveIntegerField(null=True)
    ex_level = models.PositiveIntegerField(null=True)

    @staticmethod
    @functools.lru_cache
    def max_level():
        return SkillCost.objects.aggregate(Max('target_level'))['target_level__max']

    @staticmethod
    @functools.lru_cache
    def max_ue_level():
        return UniqueEquipmentEnhanceData.objects.aggregate(Max('enhance_level'))['enhance_level__max']

    def save(self, *args, **kwargs):
        if self.star is None or self.star < self.unit.rarity:
            self.star = self.unit.rarity
        super().save(*args, **kwargs)

    def edit_json(self):
        base = model_to_dict(self)
        base["unit"] = model_to_dict(self.unit)
        base["ranks"] = [[rk.equip1, rk.equip2, rk.equip3, rk.equip4, rk.equip5, rk.equip6] for rk in self.unit.ranks.all()]
        base["max_level"] = BoxUnit.max_level()
        base["shards"] = self.box.get_item_quantity(self.unit.shard_id)
        base["max_ue_level"] = BoxUnit.max_ue_level() if self.unit.has_ue else -1
        base["max_star"] = 6 if self.unit.has_6star else 5
        return base

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['box', 'unit'], name='unique box unit')
        ]
