from django import forms

from rong.forms.fields import SelectDisplayPic, get_display_pic_choices
from rong.models import User


class PreferencesForm(forms.ModelForm):
    display_pic = forms.ChoiceField(widget=SelectDisplayPic(), choices=get_display_pic_choices(), required=True)

    class Meta:
        model = User
        fields = ['display_pic', 'single_mode']
