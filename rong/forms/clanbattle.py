from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Max, Min, F
from django.utils import timezone

from rong.forms.fields import CBLabelModelChoiceField, UnitSelect, CBLabelModelMultipleChoiceField
from rong.models import ClanBattleScore, ClanBattle
from rong.models.clan_battle_score import ClanBattleHitType
from rong.models.team import create_team


class HitForm(forms.Form):
    day = forms.IntegerField(min_value=1, max_value=31)
    member = forms.ChoiceField()
    pilot = forms.ChoiceField(required=False)
    damage = forms.IntegerField(min_value=0)
    group = CBLabelModelChoiceField(callback=lambda x: x.name, queryset=None,
                                    widget=forms.RadioSelect(attrs={'class': 'form-check-inline'}), blank=True,
                                    empty_label="None", required=False)
    tags = CBLabelModelMultipleChoiceField(callback=lambda x: x.name, queryset=None, required=False,
                                           widget=forms.SelectMultiple(attrs={'class': 'select2-multi'}))
    comp = forms.ChoiceField(required=False)
    comp_locked = forms.BooleanField(required=False)
    unit1 = UnitSelect(label='Unit 1', required=False)
    unit2 = UnitSelect(label='Unit 2', required=False)
    unit3 = UnitSelect(label='Unit 3', required=False)
    unit4 = UnitSelect(label='Unit 4', required=False)
    unit5 = UnitSelect(label='Unit 5', required=False)
    unit1_damage = forms.IntegerField(min_value=0, required=False)
    unit2_damage = forms.IntegerField(min_value=0, required=False)
    unit3_damage = forms.IntegerField(min_value=0, required=False)
    unit4_damage = forms.IntegerField(min_value=0, required=False)
    unit5_damage = forms.IntegerField(min_value=0, required=False)

    def __init__(self, hit: ClanBattleScore, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hit = hit
        hg = hit.clan_battle.hit_groups.all()
        if not hg:
            del self.fields["group"]
        else:
            self.fields["group"].queryset = hg
            if hit.id:
                self.fields["group"].initial = hit.group
        tags = hit.clan_battle.clan.hit_tags.all()
        if not tags:
            del self.fields["tags"]
        else:
            self.fields["tags"].queryset = tags
            if hit.id:
                self.fields["tags"].initial = hit.tags.all()
        member_list = list(hit.clan_battle.clan.members.select_related('user'))
        member_list.sort(key=lambda member: member.ign.lower())
        member_choices = [('', '--Select--')] + [(x.id, x.ign) for x in member_list]
        if hit.id and hit.member_id not in [x.id for x in member_list]:
            member_choices.append((hit.member_id, hit.member.ign))
        pilot_choices = [('', '(None)')] + [(x.id, x.ign) for x in member_list]
        if hit.id and hit.pilot_id and hit.pilot_id not in [x.id for x in member_list]:
            pilot_choices.append((hit.pilot_id, hit.pilot.ign))
        self.fields["member"].choices = member_choices
        self.fields["member"].widget.attrs["class"] = "select2-dd"
        self.fields["pilot"].choices = pilot_choices
        self.fields["pilot"].widget.attrs["class"] = "select2-dd"
        self.fields["pilot"].widget.attrs["placeholder"] = "(None)"
        comp_list = list(hit.clan_battle.comps.all())
        comp_list.sort(key=lambda comp: comp.name.lower())
        comp_choices = [('', 'None')] + [(x.id, x.name) for x in comp_list]
        self.fields["comp"].choices = comp_choices
        if hit.clan_battle.in_progress:
            self.fields["day"].initial = hit.clan_battle.current_day
        else:
            self.fields["day"].initial = hit.clan_battle.hits.aggregate(Max('day'))['day__max'] or 1
        self.fields["day"].widget.attrs["max"] = hit.clan_battle.total_days
        for unit in range(1, 6):
            self.fields["unit%d_damage" % unit].widget.attrs["placeholder"] = ''

        if hit.id:
            self.fields["day"].initial = hit.day
            self.fields["member"].initial = hit.member_id
            self.fields["pilot"].initial = hit.pilot_id
            self.fields["damage"].initial = hit.damage
            self.fields["comp"].initial = hit.comp_id
            self.fields["comp_locked"].initial = hit.comp_locked

            if hit.team:
                for unit in range(1, 6):
                    self.fields["unit%d" % unit].initial = getattr(hit.team, "unit%d" % unit)
                    self.fields["unit%d_damage" % unit].initial = getattr(hit, "unit%d_damage" % unit)

    def clean(self):
        cleaned_data = super().clean()
        form_errors = []
        # check day
        day = cleaned_data.get("day")
        if not day or day <= 0 or day > self.hit.clan_battle.total_days:
            self.add_error('day', "Day value out of range of days in this CB.")
        time_now = timezone.now()
        if time_now < self.hit.clan_battle.start_time:
            form_errors.append(ValidationError("Can't enter a hit before a CB has started!"))
        if day > self.hit.clan_battle.current_day:
            form_errors.append(ValidationError("Can't enter a hit for a day that hasn't started yet!"))
        # check team data
        units_filled = [cleaned_data.get("unit%d" % unit) is not None for unit in range(1, 6)]
        damages_filled = [cleaned_data.get("unit%d_damage" % unit) is not None for unit in range(1, 6)]
        if units_filled != damages_filled and sum(damages_filled) != 0:
            form_errors.append(ValidationError(
                "If you enter per-unit damage, you must enter units too and fill damage for all units."))
        if sum(damages_filled) != 0 and sum(
                [cleaned_data.get("unit%d_damage" % unit) or 0 for unit in range(1, 6)]) != cleaned_data.get("damage"):
            form_errors.append(ValidationError("Sum of individual damage must equal total damage."))
        # unit duplication check
        for first_unit in range(1, 5):
            for second_unit in range(first_unit + 1, 6):
                fu = cleaned_data.get("unit%d" % first_unit, None)
                su = cleaned_data.get("unit%d" % second_unit, None)
                if fu and su and fu == su:
                    form_errors.append(
                        ValidationError("You must be a CB2 top clan member, using two %(name)ss in the same team!",
                                        code='invalid',
                                        params={'name': fu.name}))

        # hit limit check
        if not self.hit.id and self.hit.clan_battle.member_hits_on_day(cleaned_data.get("member"), cleaned_data.get(
                "day")) >= ClanBattle.HITS_PER_DAY:
            form_errors.append(
                ValidationError("That member already has %(hits)d or more hits for this day!", code='invalid',
                                params={'hits': ClanBattle.HITS_PER_DAY}))

        if len(form_errors):
            if len(form_errors) == 1:
                raise form_errors[0]
            else:
                raise ValidationError(form_errors)
        return cleaned_data

    def save(self):
        old_day = self.hit.day
        member_changed = self.hit.member_id != int(self.cleaned_data["member"])
        damage_changed = self.hit.damage != int(self.cleaned_data["damage"])
        self.hit.day = self.cleaned_data["day"]
        self.hit.member_id = self.cleaned_data["member"]
        self.hit.pilot_id = self.cleaned_data["pilot"]
        self.hit.damage = self.cleaned_data["damage"]
        self.hit.comp_id = self.cleaned_data["comp"]
        self.hit.comp_locked = self.cleaned_data["comp_locked"]
        if "group" in self.cleaned_data:
            self.hit.group = self.cleaned_data["group"]

        # individual unit data?
        units = [x for x in (self.cleaned_data.get("unit%d" % unit) for unit in range(1, 6)) if x is not None]
        damages = [x for x in (self.cleaned_data.get("unit%d_damage" % unit) for unit in range(1, 6)) if x is not None]
        if units:
            team, ordering = create_team(units)
            self.hit.team = team
            if damages:
                for idx, dmg in enumerate(damages):
                    new_idx = ordering.index(idx)
                    setattr(self.hit, "unit%d_damage" % (new_idx + 1), dmg)
                for i in range(len(damages), 5):
                    setattr(self.hit, "unit%d_damage" % (i + 1), None)
            else:
                self.hit.clear_unit_damage()
        else:
            self.hit.team = None
            self.hit.clear_unit_damage()

        cb = self.hit.clan_battle

        # what to do about ordering?
        if self.hit.id:
            if old_day != self.hit.day:
                # Day changed - move this hit to the end of the day it moved to, then recalculate
                if old_day < self.hit.day:
                    new_order_val = cb.hits.filter(day__gt=self.hit.day).aggregate(Min('order'))['order__min']
                    if new_order_val:
                        new_order_val = new_order_val - 1
                    else:
                        new_order_val = cb.hits.count()
                    cb.hits.filter(order__gt=self.hit.order, order__lte=new_order_val).update(order=F('order') - 1)
                else:
                    new_order_val = cb.hits.filter(day__gt=self.hit.day).aggregate(Min('order'))['order__min']
                    cb.hits.filter(order__gte=new_order_val, order__lt=self.hit.order).update(order=F('order') + 1)
                self.hit.order = new_order_val
                self.hit.save()
                cb.recalculate()
            elif damage_changed or member_changed:
                # something else crucial changed, just save and recalculate
                self.hit.save()
                cb.recalculate()
            else:
                # something minor changed, just save
                self.hit.save()
        else:
            current_highest_hit_day = cb.hits.aggregate(Max('day'))['day__max'] or 0
            if self.hit.day >= current_highest_hit_day:
                # can just safely add this hit to the end using save() without an order value
                self.hit.save()
            else:
                # retroactively adding a hit to an older day - need to reorder and recalculate
                order_val = cb.hits.filter(day__gt=self.hit.day).aggregate(Min('order'))['order__min']
                cb.hits.filter(order__gte=order_val).update(order=F('order') + 1)
                self.hit.order = order_val
                # fill in the calculated fields with duds, recalculate will get them right after
                self.hit.boss_lap = 0
                self.hit.boss_number = 0
                self.hit.boss_hp_left = 0
                self.hit.hit_type = ClanBattleHitType.NORMAL
                self.hit.actual_damage = 0
                self.hit.save()
                cb.recalculate()

        if "tags" in self.cleaned_data:
            self.hit.tags.clear()
            if self.cleaned_data["tags"]:
                self.hit.tags.add(*self.cleaned_data["tags"])
