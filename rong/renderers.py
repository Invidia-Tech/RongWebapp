import bootstrap4.renderers
from django.forms import CheckboxInput


class FieldRenderer(bootstrap4.renderers.FieldRenderer):
    def append_to_checkbox_field(self, html):
        if not isinstance(self.widget, CheckboxInput):
            return html

        if '<label' in html:
            label_part = html[html.index('<label'):]
            html = html[:html.index('<label')]
        else:
            label_part = ''

        html = '<label class="form-check-label switch">' + html + '<div class="slider round"></div></label>' + label_part
        return super().append_to_checkbox_field(html)
