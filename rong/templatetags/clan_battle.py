from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

from rong.models import ClanBattle

register = template.Library()


@register.simple_tag
def user_hits_today(battle, user):
    return format_hits(battle.user_hits_today(user.id))


@register.simple_tag
def user_hits(battle, user, day):
    return format_hits(battle.user_hits_on_day(user.id, day))


@register.simple_tag
def user_hits_left_today(battle, user):
    return format_hits(ClanBattle.HITS_PER_DAY - battle.user_hits_today(user.id))


@register.simple_tag
def user_hits_left(battle, user, day):
    return format_hits(ClanBattle.HITS_PER_DAY - battle.user_hits_on_day(user.id, day))


@register.simple_tag
def user_damage_today(battle, user):
    return intcomma(battle.user_damage_dealt_today(user.id))


@register.simple_tag
def user_damage(battle, user, day):
    return intcomma(battle.user_damage_dealt_on_day(user.id, day))


@register.simple_tag
def boss_name(battle, hit):
    return getattr(battle, 'boss%d_name' % hit.boss_number)


@register.simple_tag
def boss_icon(battle, hit):
    return getattr(battle, 'boss%d_iconid' % hit.boss_number)


@register.simple_tag
def can_manage(user, entity):
    return user.can_manage(entity)


@register.simple_tag
def day_reached(battle, day):
    return day <= battle.current_day


@register.filter
def format_hits(hits):
    if float(int(hits)) == float(hits):
        return int(hits)
    return hits


@register.filter
def smallhit(damage):
    if damage < 1000:
        return int(damage)
    elif damage < 1000000:
        return '%dK' % int(damage / 1000)
    elif damage < 10000000:
        return '%.01fM' % (damage / 1000000)
    else:
        return '%dM' % int(damage / 1000000)
