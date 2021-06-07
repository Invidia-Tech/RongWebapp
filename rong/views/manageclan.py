from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from rong.decorators import login_required
from rong.models import Clan, ClanBattle


@login_required
def list_members(request, clan):
    clan = get_object_or_404(Clan, slug=clan)
    if not request.user.can_manage(clan):
        raise SuspiciousOperation()
    # do something
    clan.sync_members()
    return render(request, 'rong/manageclan/members.html', {"clan": clan})
