from django.http import HttpResponse
from django.shortcuts import render

from rong.decorators import clan_view, clanbattle_view


# Create your views here.
@clanbattle_view
def view_battle(request, battle):
    # do something
    return HttpResponse(battle.name)


@clan_view
def list_battles(request, clan):
    # do something
    ctx = {
        'in_clan': request.user.in_clan(clan),
        'clan': clan
    }
    return render(request, 'rong/clanbattle/list.html', ctx)
