from rong.models.redive_models import CNClanBattlePeriod, ENClanBattlePeriod, JPClanBattlePeriod
from django import forms
from django.conf import settings
from django.forms import RadioSelect
from django.db import models
from rong.models import User, Box, BoxUnit, ClanBattle
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
        self.fields["clan"].queryset = user.clanmember_set.select_related('clan').order_by('clan__name')
        if self.instance.id:
            # edit - clan can be its current value or any clan without an associated box
            self.fields["clan"].queryset = self.fields["clan"].queryset.filter(models.Q(box__isnull=True) | models.Q(box=self.instance))
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

def get_cb_data_source_choices():
    output = []
    for source in CB_DATA_SOURCES:
        out_choice = [source["name"], []]
        for cb_period in source["periodModel"].objects.all().order_by('id'):
            cb_id = "%s-%d" % (source["prefix"], cb_period.id)
            cb_desc = "%s CB %d (%s-%s)" % (source["name"], cb_period.id - 1000, cb_period.start_time[:cb_period.start_time.index(" ")], cb_period.end_time[:cb_period.end_time.index(" ")])
            out_choice[1].append([cb_id, cb_desc])
        output.append(out_choice)
    return output

class AddClanBattleForm(forms.ModelForm):
    class Meta:
        model = ClanBattle
        fields = ['name', 'begin_time', 'end_time']
