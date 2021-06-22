from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()


def _generate_icon(is_pfp, identifier, border=None, stars=None, mini=False):
    identifier = str(identifier)

    if identifier not in settings.SPRITE_DATA["units"]:
        raise ValueError("Identifier %s not found" % identifier)

    if border is not None:
        border_str = format_html('<i class="unit-icon-border {}"></i>',
                                 border
                                 )
    else:
        border_str = ''

    if stars is not None:
        star_str = format_html('<div class="unit-icon-stars s-{}"></div>', stars)
    else:
        star_str = ''

    if is_pfp:
        return format_html('<div class="unit-pfp u-{}">{}{}</div>',
                           identifier,
                           border_str,
                           star_str
                           )
    elif mini:
        return format_html('<div class="unit-ddicon u-{}">{}{}</div>',
                           identifier,
                           border_str,
                           star_str
                           )
    else:
        return format_html('<div class="unit-icon u-{}">{}{}</div>',
                           identifier,
                           border_str,
                           star_str
                           )


rank_colors = ["white", "blue"] + (["bronze"] * 2) + (["silver"] * 3) + (["gold"] * 4) + (["purple"] * 4)


@register.simple_tag
def box_icon(unit_id, stars, rank, **kwargs):
    star_part = 1 if stars < 3 else 3
    identifier = int(unit_id) // 100 * 100 + star_part * 10 + 1
    return _generate_icon(False, identifier, rank_colors[rank], stars)


@register.simple_tag
def unit_icon(identifier, **kwargs):
    is_pfp = kwargs.get('pfp', False)
    border = kwargs.get('border', None)
    stars = kwargs.get('stars', None)
    mini = kwargs.get('mini', False)

    return _generate_icon(is_pfp, identifier, border, stars, mini)


@register.simple_tag
def enemy_icon(identifier, **kwargs):
    alt_title = kwargs.get('alt', 'Enemy Icon')
    mini = kwargs.get('mini', False)
    if mini:
        return format_html("<img src='{0}{1}.png' alt='{2}' title='{2}' style='width: 32px; height: 32px;' />",
                           static('rong/images/enemies/'), identifier,
                           alt_title)
    else:
        return format_html("<img src='{0}{1}.png' alt='{2}' title='{2}' />", static('rong/images/enemies/'), identifier,
                           alt_title)
