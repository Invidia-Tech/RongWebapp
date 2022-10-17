from django import forms
from django.core.exceptions import ValidationError

from rong.forms.fields import UnitSelect
from rong.models import HitGroup, ClanMember, HitTag, ClanBattleComp
from rong.models.bot_models import DiscordMember
from rong.models.clan_battle import CB_DATA_SOURCES, ClanBattle
from rong.models.team import create_team


def get_cb_data_source_choices(blank_str='--Choose--'):
    output = [('', blank_str)]
    try:
        for source in CB_DATA_SOURCES:
            out_choice = [source["name"], []]
            for cb_period in source["periodModel"].objects.all().order_by('id'):
                cb_id = "%s-%d" % (source["prefix"], cb_period.id)
                cb_desc = "%s CB %d (%s-%s)" % (
                    source["name"], cb_period.id - 1000, cb_period.start_time[:cb_period.start_time.index(" ")],
                    cb_period.end_time[:cb_period.end_time.index(" ")])
                out_choice[1].append([cb_id, cb_desc])
            output.append(out_choice)
    except:
        pass
    return output


def get_discord_choices(blank_str='None'):
    output = []
    try:
        for member in DiscordMember.objects.all():
            if member.nickname is None or member.nickname == 'None' or member.nickname == member.username:
                output.append((member.member_id, '%s#%04d' % (member.username, member.discriminator)))
            else:
                output.append(
                    (member.member_id, '%s (%s#%04d)' % (member.nickname, member.username, member.discriminator)))
    except:
        pass
    output.sort(key=lambda x: x[1].lower())
    output.insert(0, ('', blank_str))
    return output


class AddClanBattleForm(forms.ModelForm):
    data_source = forms.ChoiceField(choices=get_cb_data_source_choices, required=True)

    field_order = ['name', 'start_time', 'end_time', 'viewable_by_members', 'data_source', 'boss1_name', 'boss2_name',
                   'boss3_name',
                   'boss4_name', 'boss5_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["start_time"].required = False
        self.fields["end_time"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if (not not cleaned_data["start_time"]) + (not not cleaned_data["end_time"]) == 1:
            raise ValidationError("Clan Battles must have either both dates filled in or neither date filled in.")
        return cleaned_data

    class Meta:
        model = ClanBattle
        fields = ['name', 'start_time', 'end_time', 'viewable_by_members', 'boss1_name', 'boss2_name', 'boss3_name',
                  'boss4_name',
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
            'viewable_by_members': 'Turn this off to completely hide the CB from non-leads. Should usually only be used for future CBs.',
        }


class EditClanBattleForm(forms.ModelForm):
    data_source = forms.ChoiceField(choices=get_cb_data_source_choices('Keep Current'), required=False,
                                    help_text='Optional. Current data will be kept if not selected.')

    field_order = ['name', 'start_time', 'end_time', 'data_source', 'viewable_by_members', 'boss1_name', 'boss2_name',
                   'boss3_name',
                   'boss4_name', 'boss5_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["start_time"].required = False
        self.fields["end_time"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if (not not cleaned_data["start_time"]) + (not not cleaned_data["end_time"]) == 1:
            raise ValidationError("Clan Battles must have either both dates filled in or neither date filled in.")
        return cleaned_data

    class Meta:
        model = ClanBattle
        fields = ['name', 'start_time', 'end_time', 'viewable_by_members', 'boss1_name', 'boss2_name', 'boss3_name',
                  'boss4_name',
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
            'viewable_by_members': 'Turn this off to completely hide the CB from non-leads. Should usually only be used for future CBs.',
        }


class HitGroupForm(forms.ModelForm):
    class Meta:
        model = HitGroup
        fields = ['name', 'description']


class HitTagForm(forms.ModelForm):
    class Meta:
        model = HitTag
        fields = ['name', 'description']


class ClanBattleCompForm(forms.Form):
    name = forms.CharField(max_length=50)
    boss = forms.ChoiceField()
    damage = forms.IntegerField(min_value=1, max_value=200000000)
    unit1 = UnitSelect(label='Unit 1', required=False)
    unit2 = UnitSelect(label='Unit 2', required=False)
    unit3 = UnitSelect(label='Unit 3', required=False)
    unit4 = UnitSelect(label='Unit 4', required=False)
    unit5 = UnitSelect(label='Unit 5', required=False)

    def __init__(self, comp: ClanBattleComp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comp = comp
        num_phases = self.comp.clan_battle.bosses.count()
        boss_choices = [('', '--Select--')]
        for phase in range(num_phases):
            for boss in range(1, 6):
                boss_str = chr(0x41 + phase) + str(boss)
                boss_choices.append((boss_str, boss_str))
        self.fields["boss"].choices = boss_choices

        if comp.id:
            self.fields["name"].initial = comp.name
            selected_boss_str = chr(0x40 + comp.boss_phase) + str(comp.boss_number)
            self.fields["boss"].initial = selected_boss_str
            self.fields["damage"].initial = comp.damage

            if comp.team:
                for unit in range(1, 6):
                    self.fields["unit%d" % unit].initial = getattr(comp.team, "unit%d" % unit)

    def clean(self):
        cleaned_data = super().clean()
        form_errors = []
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

        if len(form_errors):
            if len(form_errors) == 1:
                raise form_errors[0]
            else:
                raise ValidationError(form_errors)
        return cleaned_data

    def save(self):
        self.comp.name = self.cleaned_data["name"]
        self.comp.boss_phase = ord(self.cleaned_data["boss"][0]) - 0x40
        self.comp.boss_number = int(self.cleaned_data["boss"][1])
        self.comp.damage = self.cleaned_data["damage"]

        # individual unit data?
        units = [x for x in (self.cleaned_data.get("unit%d" % unit) for unit in range(1, 6)) if x is not None]
        if units:
            team, ordering = create_team(units)
            self.comp.team = team
        else:
            self.comp.team = None

        self.comp.save()


class EditClanMemberForm(forms.ModelForm):
    discord = forms.ChoiceField(choices=get_discord_choices, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ign'].widget.attrs.update({'placeholder': 'In Game Name'})
        self.fields['ign'].required = True
        self.fields['player_id'].widget.attrs.update({'placeholder': 'XXX XXX XXX'})
        self.fields['player_id'].required = False

    class Meta:
        model = ClanMember
        fields = ['ign', 'player_id']
        widgets = {
            'player_id': forms.TextInput()
        }
        labels = {
            'ign': 'IGN',
            'player_id': 'Player ID'
        }


class FullEditClanMemberForm(EditClanMemberForm):
    class Meta:
        model = ClanMember
        fields = ['ign', 'player_id', 'active', 'is_lead', 'out_of_clan']
        widgets = {
            'player_id': forms.TextInput()
        }
        labels = {
            'ign': 'IGN',
            'player_id': 'Player ID',
            'active': 'Active',
            'out_of_clan': 'Outside of Clan'
        }
