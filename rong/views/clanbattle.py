from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from rong.decorators import login_required
from rong.models import Clan, ClanBattle


# Create your views here.

def view_battle(request, battle):
    clan_battle = get_object_or_404(ClanBattle, slug=battle)
    if not request.user.can_view(clan_battle):
        raise SuspiciousOperation()
    # do something
    return HttpResponse('Pasta')


@login_required
def list_battles(request, clan):
    clan = get_object_or_404(Clan, slug=clan)
    if not request.user.can_view(clan):
        raise SuspiciousOperation()
    # do something
    return render(request, 'rong/clanbattle/list.html', {"clan": clan})
