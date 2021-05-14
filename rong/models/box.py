from django.db import models
from .redive_models import Unit
import json
import django

class Box(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def missing_units(self):
        all_unit_ids = Unit.valid_units().values_list('id', flat=True)
        current_unit_ids = self.boxunit_set.values_list('unit_id', flat=True)
        return Unit.objects.filter(id__in=(set(all_unit_ids) - set(current_unit_ids)))
    
    def unit_json(self):
        return json.dumps([unit.box_json() for unit in self.boxunit_set.all().select_related('unit')])
