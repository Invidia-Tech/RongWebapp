from django import forms
from django.db import models

from rong.forms.fields import CBLabelModelChoiceField, SimpleChoiceField
from rong.models import Box, BoxUnit


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


class CreateBoxUnitBulkForm(forms.Form):
    units = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)

    def __init__(self, box, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["units"].queryset = box.missing_units()


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


class ImportTWArmoryBoxForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea,
                           required=True,
                           label='TW Armory Export Text',
                           max_length=3000,
                           help_text='Go to the <a href="https://pcredivewiki.tw/Armory">TW Armory</a>, select '
                                     'Export&amp;Import then Export Team. Choose "Generate export text" and then copy '
                                     'the text into this box.')
    mode = SimpleChoiceField(label='Import Mode',
                             widget=forms.RadioSelect(attrs={'class': 'form-check-inline'}),
                             choices=['Overwrite', 'Update', 'Append'],
                             help_text='Overwrite = replace all data and delete any non-matching units. Update = Add '
                                       'missing units and update existing ones. Append = only add missing units, '
                                       'keep current state of units already added.',
                             initial='Update')
    refines = SimpleChoiceField(label='Refinements',
                                widget=forms.RadioSelect(attrs={'class': 'form-check-inline'}),
                                choices=['None', 'Full'],
                                initial='Full',
                                help_text='TW Armory does not track gear refinements. Choose what to do with them.')
    levels = SimpleChoiceField(label='Levels',
                               widget=forms.RadioSelect(attrs={'class': 'form-check-inline'}),
                               choices=['Keep Current', 'Update to Max'],
                               initial='Keep Current',
                               help_text='Choose what to do with unit and skill levels. If you update to max, '
                                         'you will have to re-enter any deliberately underleveled skills/units '
                                         'yourself. New units will be set to max level regardless.')
    missing_units = SimpleChoiceField(label='Missing Units',
                                      widget=forms.RadioSelect(attrs={'class': 'form-check-inline'}),
                                      choices=['Ignore', 'Error'],
                                      initial='Ignore')
