from django import forms
from django.conf import settings
from django.db import models
from django.forms import RadioSelect

from rong.models import User, Box, BoxUnit, ClanBattle, ClanMember
from rong.models.clan_battle import CB_DATA_SOURCES


def get_display_pic_choices():
    return [(x, x) for x in settings.SPRITE_DATA["units"] if x != 'unknown']


class SelectDisplayPic(RadioSelect):
    template_name = "rong/widgets/select_display_pic.html"


class PreferencesForm(forms.ModelForm):
    display_pic = forms.ChoiceField(widget=SelectDisplayPic(), choices=get_display_pic_choices(), required=True)

    class Meta:
        model = User
        fields = ['display_pic', 'single_mode']


class BoxForm(forms.ModelForm):
    clan = forms.ModelChoiceField(queryset=None, required=False, empty_label="---None---")

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
            'start_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class':'datetimefield'}),
            'end_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class':'datetimefield'})
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
    data_source = forms.ChoiceField(choices=get_cb_data_source_choices('Keep Current'), required=False, help_text='Optional. Current data will be kept if not selected.')

    field_order = ['name', 'start_time', 'end_time', 'data_source', 'boss1_name', 'boss2_name', 'boss3_name',
                   'boss4_name', 'boss5_name']

    class Meta:
        model = ClanBattle
        fields = ['name', 'start_time', 'end_time', 'boss1_name', 'boss2_name', 'boss3_name', 'boss4_name',
                  'boss5_name']
        widgets = {
            'start_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class':'datetimefield'}),
            'end_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class':'datetimefield'})
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
