from django import template

register = template.Library()


@register.filter
def get_key(d, key):
    return d.get(key, None)


@register.filter
def listize(d):
    return [d]


@register.filter
def get_item(container, key):
    if hasattr(container, key):
        return getattr(container, key)
    else:
        return container[key]
