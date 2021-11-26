from django import forms
from django.core.exceptions import ValidationError

from rong.models import HitGroup, ClanMember, HitTag
from rong.models.bot_models import DiscordMember
from rong.models.clan_battle import CB_DATA_SOURCES, ClanBattle


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
        fields = ['ign', 'player_id', 'active', 'is_lead']
        widgets = {
            'player_id': forms.TextInput()
        }
        labels = {
            'ign': 'IGN',
            'player_id': 'Player ID',
            'active': 'Active'
        }
