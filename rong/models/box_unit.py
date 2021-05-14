from django.db import models
from .redive_models import Unit, SkillCost
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.core.validators import MaxValueValidator, MinValueValidator

def valid_box_unit(value):
    if not Unit.valid_units().filter(id=value).exists():
        raise ValidationError('Unit not in game')

def valid_power(value):
    if value < 100 or value > 100000:
        raise ValidationError('Invalid unit power')

def valid_level(value):
    if value <= 0 or value > BoxUnit.max_level():
        raise ValidationError('Invalid unit level')

class BoxUnit(models.Model):
    box = models.ForeignKey('Box', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, validators=[valid_box_unit])
    power = models.PositiveIntegerField(null=True, validators=[valid_power])
    level = models.PositiveIntegerField(null=True, validators=[valid_level])
    star = models.PositiveIntegerField(null=True)
    rank = models.PositiveIntegerField(null=True)
    bond = models.PositiveIntegerField(null=True)
    # null = unequipped or not specified, 0-5 = refinement stars
    equip1 = models.PositiveIntegerField(null=True)
    equip2 = models.PositiveIntegerField(null=True)
    equip3 = models.PositiveIntegerField(null=True)
    equip4 = models.PositiveIntegerField(null=True)
    equip5 = models.PositiveIntegerField(null=True)
    equip6 = models.PositiveIntegerField(null=True)

    def max_level():
        return SkillCost.objects.aggregate(Max('target_level'))['target_level__max']
    
    def save(self, *args, **kwargs):
        if self.star is None:
            self.star = self.unit.rarity
        super().save(*args, **kwargs)

    def box_json(self):
        return {"id": self.id, "unit_id": self.unit_id, "name": self.unit.name, "range": self.unit.search_area_width, "star": self.star, "rank": self.rank}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['box', 'unit'], name='unique box unit')
        ]
