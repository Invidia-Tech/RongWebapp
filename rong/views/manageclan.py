from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from rong.decorators import login_required
from rong.models import Clan


@login_required
def list_members(request, clan):
    clan = get_object_or_404(Clan, slug=clan)
    if not request.user.can_manage(clan):
        raise PermissionDenied()
    # do something
    clan.sync_members()
    return render(request, 'rong/manageclan/members.html', {"clan": clan})
