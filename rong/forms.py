from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max, Min, F
from django.forms import RadioSelect
from django.utils import timezone

from rong.models import User, Box, BoxUnit, ClanBattle, ClanMember, Unit, ClanBattleScore
from rong.models.clan_battle import CB_DATA_SOURCES
from rong.models.clan_battle_score import ClanBattleHitType
from rong.models.team import create_team


def get_display_pic_choices():
    return [(x, x) for x in settings.SPRITE_DATA["units"] if x != 'unknown']


class SelectDisplayPic(RadioSelect):
    template_name = "rong/widgets/select_display_pic.html"


class CBLabelModelChoiceField(forms.ModelChoiceField):
    def __init__(self, callback=None, *args, **kwargs):
        super(CBLabelModelChoiceField, self).__init__(*args, **kwargs)
        self.callback = callback

    def label_from_instance(self, obj):
        return self.callback(obj)


class UnitSelect(CBLabelModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['callback'] = lambda u: u.name
        kwargs['queryset'] = Unit.valid_units()
        super(UnitSelect, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] = 'unit-selector'


class PreferencesForm(forms.ModelForm):
    display_pic = forms.ChoiceField(widget=SelectDisplayPic(), choices=get_display_pic_choices(), required=True)

    class Meta:
        model = User
        fields = ['display_pic', 'single_mode']


class BoxForm(forms.ModelForm):
    clan = CBLabelModelChoiceField(queryset=None, required=False, empty_label="---None---",
                                   callback=lambda cm: cm.clan.name)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["clan"].queryset = user.clan_memberships.select_related('clan').order_by('clan__name')
        if self.instance.id:
            # edit - clan can be its current value or any clan without an associated box
            self.fields["clan"].queryset = self.fields["clan"].queryset.filter(
                models.Q(box__isnull=True) | models.Q(box=self.instance))
        else:
            # create - clan can be any clan without an associated box
            self.fields["clan"].queryset = self.fields["clan"].queryset.filter(box__isnull=True)
            self.instance.user = user

    class Meta:
        model = Box
        fields = ['name']


class CreateBoxUnitForm(forms.ModelForm):
    class Meta:
        model = BoxUnit
        fields = ['unit']


class EditBoxUnitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for equip in range(1, 7):
            self.fields["equip%d" % equip].required = False

    class Meta:
        model = BoxUnit
        fields = ['level', 'star', 'rank', 'equip1', 'equip2', 'equip3', 'equip4', 'equip5', 'equip6']


def get_cb_data_source_choices(blank_str='--Choose--'):
    output = [('', blank_str)]
    for source in CB_DATA_SOURCES:
        out_choice = [source["name"], []]
        for cb_period in source["periodModel"].objects.all().order_by('id'):
            cb_id = "%s-%d" % (source["prefix"], cb_period.id)
            cb_desc = "%s CB %d (%s-%s)" % (
                source["name"], cb_period.id - 1000, cb_period.start_time[:cb_period.start_time.index(" ")],
                cb_period.end_time[:cb_period.end_time.index(" ")])
            out_choice[1].append([cb_id, cb_desc])
        output.append(out_choice)
    return output


class AddClanBattleForm(forms.ModelForm):
    data_source = forms.ChoiceField(choices=get_cb_data_source_choices, required=True)

    field_order = ['name', 'start_time', 'end_time', 'data_source', 'boss1_name', 'boss2_name', 'boss3_name',
                   'boss4_name', 'boss5_name']

    class Meta:
        model = ClanBattle
        fields = ['name', 'start_time', 'end_time', 'boss1_name', 'boss2_name', 'boss3_name', 'boss4_name',
                  'boss5_name']
        widgets = {
            'start_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'}),
            'end_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'})
        }
        labels = {
            'start_time': 'Start Date/Time (UTC)',
            'end_time': 'End Date/Time (UTC)',
            'boss1_name': 'Boss 1 Name',
            'boss2_name': 'Boss 2 Name',
            'boss3_name': 'Boss 3 Name',
            'boss4_name': 'Boss 4 Name',
            'boss5_name': 'Boss 5 Name',
        }
        help_texts = {
            'boss1_name': 'Leave blank to load from boss data',
            'boss2_name': 'Leave blank to load from boss data',
            'boss3_name': 'Leave blank to load from boss data',
            'boss4_name': 'Leave blank to load from boss data',
            'boss5_name': 'Leave blank to load from boss data',
        }


class EditClanBattleForm(forms.ModelForm):
    data_source = forms.ChoiceField(choices=get_cb_data_source_choices('Keep Current'), required=False,
                                    help_text='Optional. Current data will be kept if not selected.')

    field_order = ['name', 'start_time', 'end_time', 'data_source', 'boss1_name', 'boss2_name', 'boss3_name',
                   'boss4_name', 'boss5_name']

    class Meta:
        model = ClanBattle
        fields = ['name', 'start_time', 'end_time', 'boss1_name', 'boss2_name', 'boss3_name', 'boss4_name',
                  'boss5_name']
        widgets = {
            'start_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'}),
            'end_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'})
        }
        labels = {
            'start_time': 'Start Date/Time (UTC)',
            'end_time': 'End Date/Time (UTC)',
            'boss1_name': 'Boss 1 Name',
            'boss2_name': 'Boss 2 Name',
            'boss3_name': 'Boss 3 Name',
            'boss4_name': 'Boss 4 Name',
            'boss5_name': 'Boss 5 Name',
        }
        help_texts = {
            'boss1_name': 'Empty to load from boss data',
            'boss2_name': 'Empty to load from boss data',
            'boss3_name': 'Empty to load from boss data',
            'boss4_name': 'Empty to load from boss data',
            'boss5_name': 'Empty to load from boss data',
        }


class EditClanMemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ign'].widget.attrs.update({'placeholder': 'In Game Name'})
        self.fields['ign'].required = False
        self.fields['player_id'].widget.attrs.update({'placeholder': 'XXX XXX XXX'})
        self.fields['player_id'].required = False
        self.fields['group_num'].widget.attrs.update({'placeholder': ''})
        self.fields['group_num'].required = False

    class Meta:
        model = ClanMember
        fields = ['ign', 'player_id', 'group_num']
        widgets = {
            'player_id': forms.TextInput()
        }
        labels = {
            'ign': 'IGN',
            'player_id': 'Player ID',
            'group_num': 'Group #'
        }


class FullEditClanMemberForm(EditClanMemberForm):
    class Meta:
        model = ClanMember
        fields = ['ign', 'player_id', 'group_num', 'is_lead']
        widgets = {
            'player_id': forms.TextInput()
        }
        labels = {
            'ign': 'IGN',
            'player_id': 'Player ID',
            'group_num': 'Group #'
        }


class HitForm(forms.Form):
    day = forms.IntegerField(min_value=1, max_value=31)
    user = forms.ChoiceField()
    damage = forms.IntegerField(min_value=0)
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
        member_list = list(hit.clan_battle.clan.members.select_related('user'))
        member_list.sort(key=lambda member: member.user_display_name)
        choices = [('', '--Select--')] + [(x.user_id, x.user_display_name) for x in member_list]
        if hit.id and hit.user_id not in [x.user_id for x in member_list]:
            if hit.ign:
                choices.append((hit.user_id, "%s (%s#%04d)" % (hit.ign, hit.user.name, hit.user.discriminator)))
            else:
                choices.append((hit.user_id, "%s#%04d" % (hit.user.name, hit.user.discriminator)))
        self.fields["user"].choices = choices
        if hit.clan_battle.in_progress:
            self.fields["day"].initial = hit.clan_battle.current_day
        else:
            self.fields["day"].initial = hit.clan_battle.hits.aggregate(Max('day'))['day__max'] or 1
        self.fields["day"].widget.attrs["max"] = hit.clan_battle.total_days
        for unit in range(1, 6):
            self.fields["unit%d_damage" % unit].widget.attrs["placeholder"] = ''

        if hit.id:
            self.fields["day"].initial = hit.day
            self.fields["user"].initial = hit.user_id
            self.fields["damage"].initial = hit.damage

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
        if not self.hit.id and self.hit.clan_battle.user_hits_on_day(cleaned_data.get("user"), cleaned_data.get(
                "day")) >= ClanBattle.HITS_PER_DAY:
            form_errors.append(
                ValidationError("That user already has %(hits)d or more hits for this day!", code='invalid',
                                params={'hits': ClanBattle.HITS_PER_DAY}))

        if len(form_errors):
            if len(form_errors) == 1:
                raise form_errors[0]
            else:
                raise ValidationError(form_errors)
        return cleaned_data

    def save(self):
        old_day = self.hit.day
        user_changed = self.hit.user_id != self.cleaned_data["user"]
        damage_changed = self.hit.damage != self.cleaned_data["damage"]
        self.hit.day = self.cleaned_data["day"]
        self.hit.user_id = self.cleaned_data["user"]
        self.hit.damage = self.cleaned_data["damage"]

        # individual unit data?
        units = [x for x in (self.cleaned_data.get("unit%d" % unit) for unit in range(1, 6)) if x is not None]
        damages = [x for x in (self.cleaned_data.get("unit%d_damage" % unit) for unit in range(1, 6)) if x is not None]
        if units:
            team, ordering = create_team(units)
            team.save()
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

        # get ign if available
        cb = self.hit.clan_battle
        cm = cb.clan.members.filter(user_id=self.hit.user_id).first()
        self.hit.ign = cm.ign if cm else None

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
                    cb.hits.filter(order__gte=new_order_val,order__lt=self.hit.order).update(order=F('order') + 1)
                self.hit.order = new_order_val
                self.hit.save()
                cb.recalculate()
            elif damage_changed or user_changed:
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
