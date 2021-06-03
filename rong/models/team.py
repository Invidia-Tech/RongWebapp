from rong.models.redive_models import Unit
from django.db import models
from typing import Optional


class Team(models.Model):
    power = models.PositiveIntegerField(null=True)
    unit1 = models.ForeignKey(
        'Unit', related_name='unit1teams', on_delete=models.DO_NOTHING)
    unit1_star = models.PositiveIntegerField(null=True)
    unit1_level = models.PositiveIntegerField(null=True)
    unit2 = models.ForeignKey(
        'Unit', related_name='unit2teams', on_delete=models.DO_NOTHING)
    unit2_star = models.PositiveIntegerField(null=True)
    unit2_level = models.PositiveIntegerField(null=True)
    unit3 = models.ForeignKey(
        'Unit', related_name='unit3teams', on_delete=models.DO_NOTHING)
    unit3_star = models.PositiveIntegerField(null=True)
    unit3_level = models.PositiveIntegerField(null=True)
    unit4 = models.ForeignKey(
        'Unit', related_name='unit4teams', on_delete=models.DO_NOTHING)
    unit4_star = models.PositiveIntegerField(null=True)
    unit4_level = models.PositiveIntegerField(null=True)
    unit5 = models.ForeignKey(
        'Unit', related_name='unit5teams', on_delete=models.DO_NOTHING)
    unit5_level = models.PositiveIntegerField(null=True)
    unit5_star = models.PositiveIntegerField(null=True)
    uid = models.BigIntegerField(db_index=True)

    def create_team(units, stars=None, levels=None, power=None):
        t = Team(power=power)
        unit_data = [{"unit": units[u], "star": None if stars is None else stars[u],
                      "level": None if levels is None else levels[u]} for u in range(5)]
        unit_data.sort(key=lambda x: x["unit"].search_area_width)
        for unit, data in enumerate(unit_data):
            setattr(t, 'unit%d' % (unit+1), data["unit"])
            setattr(t, 'unit%d_star' % (unit+1), data["star"])
            setattr(t, 'unit%d_level' % (unit+1), data["level"])
        return t
