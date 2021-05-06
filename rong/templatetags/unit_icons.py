from django import template
from django.utils.html import format_html, mark_safe
from django.templatetags.static import static
import json

register = template.Library()
position_cache = None

@register.simple_tag(takes_context=True)
def unit_icon(context, identifier, size, is_round=False, margin='2px 2px 3px'):
    sheet_url = static('rong/icon_sheet.webp') if context.get('supports_webp', False) else static('rong/icon_sheet.jpg')
    global position_cache
    if position_cache is None:
        with open('assets/icons/sheet_positions.json', 'r', encoding='utf-8') as fh:
            position_cache = json.load(fh)
    
    if identifier not in position_cache:
        raise ValueError("Identifier %s not found" % identifier)
    
    if is_round:
        return format_html('<div style="width: {}px; height: {}px; background-image: url(\'{}\'); background-size: {}px; border-radius: {}px; border: 1px solid transparent; display: inline-block; margin: {}; background-position: -{}px -{}px;"></div>',
            size,
            size,
            sheet_url,
            640 * size // 64,
            size // 2,
            mark_safe(margin),
            position_cache[identifier][0] * size // 64,
            position_cache[identifier][1] * size // 64
        )
    else:
        return format_html('<div style="width: {}px; height: {}px; background-image: url(\'{}\'); background-size: {}px; display: inline-block; margin: {}; background-position: -{}px -{}px;"></div>',
            size,
            size,
            sheet_url,
            640 * size // 64,
            mark_safe(margin),
            position_cache[identifier][0] * size // 64,
            position_cache[identifier][1] * size // 64
        )
