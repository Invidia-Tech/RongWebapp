from django import template

register = template.Library()


@register.simple_tag
def equip_star_range():
    return range(1, 5 + 1)


@register.simple_tag
def unit_star_range():
    return range(1, 6 + 1)


@register.simple_tag
def equip_range():
    return range(1, 6 + 1)


@register.simple_tag
def equip_align(slot):
    if slot == 3:
        return 'left'
    elif slot == 4:
        return 'right'
    else:
        return 'center'


@register.simple_tag
def equip_size(slot):
    if slot == 3 or slot == 4:
        return '4'
    else:
        return '6'
