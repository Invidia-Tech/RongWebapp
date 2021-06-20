from django.shortcuts import render

from rong.decorators import clan_view, clanbattle_view


# Create your views here.
from rong.models import ClanBattle


@clanbattle_view
def view_battle(request, battle : ClanBattle):
    ctx = {
        'in_clan': request.user.in_clan(battle.clan),
        'battle': battle,
        'hits': battle.hits.prefetch_related('user').order_by('-order')[:30],
        'myhits': battle.hits.filter(user=request.user).order_by('-order')[:30],
    }
    return render(request, 'rong/clanbattle/view.html', ctx)


@clan_view
def list_battles(request, clan):
    # do something
    ctx = {
        'in_clan': request.user.in_clan(clan),
        'clan': clan
    }
    return render(request, 'rong/clanbattle/list.html', ctx)
