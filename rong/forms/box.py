from django import forms

from rong.forms.fields import SimpleChoiceField
from rong.models import Box, BoxUnit


class BoxForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.id:
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
    shards = forms.IntegerField(min_value=0, max_value=9999)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for equip in range(1, 7):
            self.fields["equip%d" % equip].required = False
        self.fields["ue_level"].required = False
        self.fields["notes"].required = False

    class Meta:
        model = BoxUnit
        fields = ['level', 'star', 'rank', 'equip1', 'equip2', 'equip3', 'equip4', 'equip5', 'equip6', 'ue_level',
                  'notes']


class ImportTWArmoryBoxForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea,
                           required=True,
                           label='TW Armory Export Text',
                           max_length=8000,
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


class ImportLoadIndexBoxForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea,
                           required=True,
                           label='Load Index Text',
                           max_length=200000,
                           help_text='Acquire your /load/index response via whatever means...')
