from django import template

from rong.models import ClanBattle

register = template.Library()


@register.simple_tag
def user_hits_today(battle, user):
    return _format_hits(battle.user_hits_today(user.id))


@register.simple_tag
def user_hits(battle, user, day):
    return _format_hits(battle.user_hits_on_day(user.id, day))


@register.simple_tag
def user_hits_left_today(battle, user):
    return _format_hits(ClanBattle.HITS_PER_DAY - battle.user_hits_today(user.id))


@register.simple_tag
def user_hits_left(battle, user, day):
    return _format_hits(ClanBattle.HITS_PER_DAY - battle.user_hits_on_day(user.id, day))


@register.simple_tag
def user_damage_today(battle, user):
    return battle.user_damage_dealt_today(user.id)


@register.simple_tag
def user_damage(battle, user, day):
    return battle.user_damage_dealt_on_day(user.id, day)


@register.simple_tag
def boss_name(battle, hit):
    return getattr(battle, 'boss%d_name' % hit.boss_number)

def _format_hits(hits):
    if float(int(hits)) == float(hits):
        return int(hits)
    return hits

@register.filter
def format_hits(hits):
    return _format_hits(hits)
