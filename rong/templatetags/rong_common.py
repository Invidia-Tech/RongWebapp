from django import template

register = template.Library()


@register.filter
def get_key(d, key):
    return d.get(key, None)
