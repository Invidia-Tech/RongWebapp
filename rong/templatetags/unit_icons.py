from django import template
from django.utils.html import format_html, mark_safe
from django.templatetags.static import static
from django.conf import settings
import os.path
import json

register = template.Library()
position_cache = None

@register.simple_tag(takes_context=True)
def unit_icon(context, identifier, size, **kwargs):
    is_round = kwargs.get('round', False)
    margin = kwargs.get('margin', '0')
    border = kwargs.get('border', None)
    stars = kwargs.get('stars', None)
    selectable = kwargs.get('selectable', False)

    sheet_url = static('rong/images/icon_sheet.webp') if context.get('supports_webp', False) else static('rong/images/icon_sheet.jpg')
    global position_cache
    if position_cache is None:
        with open(os.path.join(settings.BASE_DIR, 'assets/icons/sheet_positions.json'), 'r', encoding='utf-8') as fh:
            position_cache = json.load(fh)
    
    if identifier not in position_cache:
        raise ValueError("Identifier %s not found" % identifier)
    
    if selectable:
        border_str = format_html('<img class="selectable-icon-border" src="{}" style="width: {}px; height: {}px;" />', static('rong/images/border_white.png'), size, size)
    elif border is not None:
        border_str = format_html('<img src="{}" style="width: {}px; height: {}px;" />', static('rong/images/border_%s.png' % border), size, size)
    else:
        border_str = ''

    if stars is not None:
        filled_star = format_html('<img src="{}" style="width: {}px; height: {}px;" />', static('rong/images/star_on.png'), round(size*0.15), round(size*0.15))
        unfilled_star = format_html('<img src="{}" style="width: {}px; height: {}px;" />', static('rong/images/star_off.png'), round(size*0.15), round(size*0.15))
        star_imgs = mark_safe((filled_star * stars) + (unfilled_star * (5 - stars)))
        star_str = format_html('<div class="stars">{}</div>', star_imgs)
    else:
        star_str = ''

    
    if is_round:
        return format_html('<div class="unit-icon" style="width: {}px; height: {}px; background-image: url(\'{}\'); background-size: {}px; border-radius: {}px; border: 1px solid transparent; margin: {}; background-position: -{}px -{}px;">{}{}</div>',
            size,
            size,
            sheet_url,
            640 * size // 64,
            size // 2,
            mark_safe(margin),
            position_cache[identifier][0] * size // 64,
            position_cache[identifier][1] * size // 64,
            border_str,
            star_str
        )
    else:
        return format_html('<div class="unit-icon" style="width: {}px; height: {}px; background-image: url(\'{}\'); background-size: {}px; margin: {}; background-position: -{}px -{}px;">{}{}</div>',
            size,
            size,
            sheet_url,
            640 * size // 64,
            mark_safe(margin),
            position_cache[identifier][0] * size // 64,
            position_cache[identifier][1] * size // 64,
            border_str,
            star_str
        )
