from django.db import models
from django.utils.functional import cached_property

from rong.mixins import ModelDiffMixin


def create_team(units, stars=None, levels=None, power=None):
    assert len(units) and len(units) <= 5
    assert stars is None or len(stars) == len(units)
    assert levels is None or len(levels) == len(units)

    t = Team(power=power, uid=1)
    for u in range(5):
        setattr(t, "unit%d" % (u+1), None if u >= len(units) else units[u])
        setattr(t, "unit%d_star" % (u+1), None if (stars is None or u >= len(units)) else stars[u])
        setattr(t, 'unit%d_level' % (u + 1), None if (levels is None or u >= len(units)) else levels[u])

    order_map = t.order_units()
    duplicate = t.find_duplicate()
    if duplicate:
        return duplicate, order_map
    else:
        t.save()
        return t, order_map


class Team(models.Model, ModelDiffMixin):
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

    def find_duplicate(self):
        params = dict(self.__dict__)
        for field in ["_state", "_ModelDiffMixin__initial", "id"]:
            if field in params:
                del params[field]
        if self.id:
            params["id__lt"] = self.id
        return Team.objects.filter(**params).order_by('id').first()

    def fix(self):
        order_map = self.order_units()
        if self.has_changed:
            print("Team %d: order corrected" % self.id)
            self.save()
            for score in self.clanbattlescore_set.all():
                damages = [getattr(score, "unit%d_damage" % (u+1)) for u in range(5)]
                for idx, dmg in enumerate(damages):
                    new_idx = order_map.index(idx)
                    setattr(score, "unit%d_damage" % (new_idx + 1), dmg)
                if score.has_changed:
                    score.save()

    def deduplicate(self):
        dupe = self.find_duplicate()
        if dupe:
            print("Deduplicating %d => %d" % (self.id, dupe.id))
            for score in self.clanbattlescore_set.all():
                score.team = dupe
                score.save()
            for comp in self.clanbattlecomp_set.all():
                comp.team = dupe
                comp.save()
            self.delete()

    def order_units(self):
        unit_data = [{
            "unit": getattr(self, "unit%d" % (u + 1)),
            "star": getattr(self, "unit%d_star" % (u + 1)),
            "level": getattr(self, "unit%d_level" % (u + 1)),
            "original_index": u
        } for u in range(5)]
        unit_data.sort(key=lambda x: (x["unit"].sort_key if x["unit"] is not None else 999999))
        uid = 1
        for unit, data in enumerate(unit_data):
            setattr(self, 'unit%d' % (unit + 1), data["unit"])
            setattr(self, 'unit%d_star' % (unit + 1), data["star"])
            setattr(self, 'unit%d_level' % (unit + 1), data["level"])
            uid *= data["unit"].prime if data["unit"] is not None else 1
        self.uid = uid
        return [unit_data[n]["original_index"] for n in range(5)]

    def fix_uid(self):
        uid = 1
        for unit in range(5):
            unit_data = getattr(self, 'unit%d' % (unit + 1))
            uid *= unit_data.prime if unit_data is not None else 1
        if self.uid != uid:
            print("Team %d: UID %d => %d" % (self.id, self.uid, uid))
            self.uid = uid
            self.save()
