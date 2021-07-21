from django import forms
from django.conf import settings

from rong.models import Unit


def get_display_pic_choices():
    return [(x, x) for x in settings.SPRITE_DATA["units"] if x != 'unknown']


class SelectDisplayPic(forms.RadioSelect):
    template_name = "rong/widgets/select_display_pic.html"


class CBLabelModelChoiceField(forms.ModelChoiceField):
    def __init__(self, callback=None, *args, **kwargs):
        super(CBLabelModelChoiceField, self).__init__(*args, **kwargs)
        self.callback = callback

    def label_from_instance(self, obj):
        return self.callback(obj)


class SimpleChoiceField(forms.ChoiceField):
    def __init__(self, choices, **kwargs):
        choices = [(n, n) for n in choices]
        super().__init__(choices=choices, **kwargs)


class UnitSelect(CBLabelModelChoiceField):
    unit_choices = None

    def __init__(self, *args, **kwargs):
        kwargs['callback'] = lambda u: u.name
        kwargs['queryset'] = Unit.valid_units()
        super(UnitSelect, self).__init__(*args, **kwargs)
        if not UnitSelect.unit_choices:
            try:
                UnitSelect.unit_choices = list(CBLabelModelChoiceField(lambda u: u.name, Unit.valid_units()).choices)
            except:
                UnitSelect.unit_choices = [('', 'N/A')]
        self.choices = UnitSelect.unit_choices
        self.widget.attrs['class'] = 'unit-selector'
