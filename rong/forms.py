from django import forms
from django.conf import settings
from django.forms import RadioSelect

def get_display_pic_choices():
    return [(x, x) for x in settings.UNIT_ICON_POSITIONS if x != 'unknown']

class SelectDisplayPic(RadioSelect):
    template_name = "rong/widgets/select_display_pic.html"

class SelectDisplayPicWebP(RadioSelect):
    template_name = "rong/widgets/select_display_pic_webp.html"

class PreferencesForm(forms.Form):
    display_pic = forms.ChoiceField(widget=SelectDisplayPic(), choices=get_display_pic_choices(), required=True)
    single_mode = forms.BooleanField(required=False)

    def __init__(self, request, data=None, initial=None):
        super().__init__(data=data, initial=initial)
        # hacky thing to make webp usable in the display pic selection
        if request.supports_webp:
            old_choices = self.fields["display_pic"].widget.choices
            self.fields["display_pic"].widget = SelectDisplayPicWebP()
            self.fields["display_pic"].widget.choices = old_choices
