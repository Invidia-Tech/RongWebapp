from functools import wraps

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from rong.forms import EditClanMemberForm, FullEditClanMemberForm
from rong.models import Clan


def clan_lead_required(func):
    @wraps(func)
    def _wrapped_view(request, clan, *args, **kwargs):
        clan = get_object_or_404(Clan, slug=clan)
        if request.user.is_authenticated and request.user.can_manage(clan):
            return func(request, clan, *args, **kwargs)
        raise PermissionDenied()

    return _wrapped_view


def member_form(request, clan):
    if request.user.can_administrate(clan):
        return FullEditClanMemberForm
    else:
        return EditClanMemberForm

@clan_lead_required
def edit_member(request, clan, member_id):
    member = get_object_or_404(clan.members, pk=member_id)
    form_class = member_form(request, clan)
    if request.method == 'POST':
        form = form_class(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "member": member.json})
        else:
            return JsonResponse({"success": False, "error": "Invalid member"})
    elif request.method == 'GET':
        return JsonResponse(member.json)
    else:
        raise SuspiciousOperation()


@clan_lead_required
def list_members(request, clan):
    clan.sync_members()
    ctx = {
        "clan": clan,
        "form": member_form(request, clan)()
    }
    return render(request, 'rong/manageclan/members.html', ctx)
