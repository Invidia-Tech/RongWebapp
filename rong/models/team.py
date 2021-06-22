from django.db import models
from django.utils.functional import cached_property


def create_team(units, stars=None, levels=None, power=None):
    assert len(units) and len(units) <= 5
    assert stars is None or len(stars) == len(units)
    assert levels is None or len(levels) == len(units)

    params = {"power": power, "uid": 0}  # TODO
    unit_data = [{
        "unit": None if u >= len(units) else units[u],
        "star": None if (stars is None or u >= len(units)) else stars[u],
        "level": None if (levels is None or u >= len(units)) else levels[u],
        "original_index": u
    } for u in range(5)]
    unit_data.sort(key=lambda x: (x["unit"].search_area_width if x["unit"] is not None else 9999))
    for unit, data in enumerate(unit_data):
        params['unit%d' % (unit + 1)] = data["unit"]
        params['unit%d_star' % (unit + 1)] = data["star"]
        params['unit%d_level' % (unit + 1)] = data["level"]
    t = Team.objects.filter(**params).first()
    if not t:
        t = Team(**params)
        t.save()
    return t, [unit_data[n]["original_index"] for n in range(len(units))]


class Team(models.Model):
    power = models.PositiveIntegerField(null=True)
    unit1 = models.ForeignKey(
        'Unit', related_name='unit1teams', on_delete=models.DO_NOTHING, null=True)
    unit1_star = models.PositiveIntegerField(null=True)
    unit1_level = models.PositiveIntegerField(null=True)
    unit2 = models.ForeignKey(
        'Unit', related_name='unit2teams', on_delete=models.DO_NOTHING, null=True)
    unit2_star = models.PositiveIntegerField(null=True)
    unit2_level = models.PositiveIntegerField(null=True)
    unit3 = models.ForeignKey(
        'Unit', related_name='unit3teams', on_delete=models.DO_NOTHING, null=True)
    unit3_star = models.PositiveIntegerField(null=True)
    unit3_level = models.PositiveIntegerField(null=True)
    unit4 = models.ForeignKey(
        'Unit', related_name='unit4teams', on_delete=models.DO_NOTHING, null=True)
    unit4_star = models.PositiveIntegerField(null=True)
    unit4_level = models.PositiveIntegerField(null=True)
    unit5 = models.ForeignKey(
        'Unit', related_name='unit5teams', on_delete=models.DO_NOTHING, null=True)
    unit5_level = models.PositiveIntegerField(null=True)
    unit5_star = models.PositiveIntegerField(null=True)
    uid = models.BigIntegerField(db_index=True)

    @cached_property
    def units(self):
        ret = []
        for unit in range(1, 6):
            u_data = getattr(self, "unit%d" % unit)
            if u_data:
                ret.append({
                    "unit": u_data.id,
                    "icon": u_data.id + (10 if u_data.rarity < 3 else 30),
                    "name": u_data.name,
                    "star": getattr(self, "unit%d_star" % unit),
                    "level": getattr(self, "unit%d_level" % unit),
                })
        ret.reverse()
        return ret
