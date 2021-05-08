from django import template
from django.utils.html import format_html, mark_safe
from django.templatetags.static import static
from django.conf import settings
import os.path
import json

register = template.Library()

def _generate_icon(sheet, is_round, identifier, size, border=None, margin='0', stars=None):
    identifier = str(identifier)

    if identifier not in settings.UNIT_ICON_POSITIONS:
        raise ValueError("Identifier %s not found" % identifier)
    
    if border is not None:
        border_str = format_html('<img src="{}" style="width: {}px; height: {}px; border-radius: {}px;" />',
            static('rong/images/border_%s.png' % border),
            size,
            size,
            size * 5 // 64
        )
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
            sheet,
            640 * size // 64,
            size // 2,
            mark_safe(margin),
            settings.UNIT_ICON_POSITIONS[identifier][0] * size // 64,
            settings.UNIT_ICON_POSITIONS[identifier][1] * size // 64,
            border_str,
            star_str
        )
    else:
        return format_html('<div class="unit-icon" style="width: {}px; height: {}px; background-image: url(\'{}\'); background-size: {}px; margin: {}; background-position: -{}px -{}px;">{}{}</div>',
            size,
            size,
            sheet,
            640 * size // 64,
            mark_safe(margin),
            settings.UNIT_ICON_POSITIONS[identifier][0] * size // 64,
            settings.UNIT_ICON_POSITIONS[identifier][1] * size // 64,
            border_str,
            star_str
        )

rank_colors = ["white", "blue"] + (["bronze"] * 2) + (["silver"] * 3) + (["gold"] * 4) + (["purple"] * 4)

@register.simple_tag(takes_context=True)
def box_icon(context, unit_id, stars, rank, **kwargs):
    size = kwargs.get('size', 64)
    margin = kwargs.get('margin', '0')
    use_webp = kwargs.get('webp', None)

    if use_webp or (use_webp is None and context.get('supports_webp', False)):
        sheet = static('rong/images/icon_sheet.webp')
    else:
        sheet = static('rong/images/icon_sheet.png')
    
    star_part = 1 if stars < 3 else 3
    identifier = int(unit_id)//100*100 + star_part*10 + 1
    return _generate_icon(sheet, False, identifier, size, rank_colors[rank], margin, stars)

@register.simple_tag(takes_context=True)
def unit_icon(context, identifier, size, **kwargs):
    is_round = kwargs.get('round', False)
    margin = kwargs.get('margin', '0')
    border = kwargs.get('border', None)
    stars = kwargs.get('stars', None)
    selectable = kwargs.get('selectable', False)
    use_webp = kwargs.get('webp', None)

    if selectable and border is not None:
        raise ValueError("Cannot specify both selectable and border")
    
    if selectable:
        border = 'white'

    if use_webp or (use_webp is None and context.get('supports_webp', False)):
        sheet = static('rong/images/icon_sheet.webp')
    else:
        sheet = static('rong/images/icon_sheet.jpg') if is_round else static('rong/images/icon_sheet.png')
    
    return _generate_icon(sheet, is_round, identifier, size, border, margin, stars)
