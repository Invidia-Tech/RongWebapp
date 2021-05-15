from django import forms
from django.conf import settings
from django.forms import RadioSelect
from rong.models import User, Box, BoxUnit

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
