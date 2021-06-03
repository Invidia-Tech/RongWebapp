from django import template
from django.utils.html import json_script

from rong.models import UnitAlias

register = template.Library()

@register.simple_tag
def nicknames():
    nicks = [{"unit": str(alias.unit_id), "name": alias.name.capitalize()} for alias in UnitAlias.objects.all()]
    return json_script(nicks, 'unitNicknames')
