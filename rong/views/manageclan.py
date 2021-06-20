from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from rong.decorators import clan_lead_view
from rong.forms import EditClanMemberForm, FullEditClanMemberForm, AddClanBattleForm, EditClanBattleForm
from rong.models import ClanBattle


@clan_lead_view
def edit_battle(request, clan, battle_id):
    battle = get_object_or_404(clan.clanbattle_set, pk=battle_id)
    if request.method == 'POST':
        form = EditClanBattleForm(request.POST, instance=battle)
        if form.is_valid():
            form.save()
            if "data_source" in form.data and form.data["data_source"]:
                battle.load_boss_info(form.data["data_source"])
                battle.recalculate()
            messages.add_message(request, messages.SUCCESS, "Clan Battle successfully edited.")
            return redirect('rong:clan_list_battles', clan.slug)
    else:
        form = EditClanBattleForm(instance=battle)
    ctx = {
        'form': form,
        'clan': clan
    }
    return render(request, 'rong/manageclan/edit_battle.html', ctx)


@clan_lead_view
def add_battle(request, clan):
    if request.method == 'POST':
        cb = ClanBattle(clan=clan)
        form = AddClanBattleForm(request.POST, instance=cb)
        if form.is_valid():
            form.save()
            cb.load_boss_info(form.data["data_source"])
            cb.recalculate()
            messages.add_message(request, messages.SUCCESS, "Clan Battle successfully added.")
            return redirect('rong:clan_list_battles', clan.slug)
    else:
        form = AddClanBattleForm()
    ctx = {
        'form': form,
        'clan': clan
    }
    return render(request, 'rong/manageclan/add_battle.html', ctx)


@clan_lead_view
def list_battles(request, clan):
    ctx = {
        "clan": clan,
    }
    return render(request, 'rong/manageclan/battles.html', ctx)


def member_form(request, clan):
    if request.user.can_administrate(clan):
        return FullEditClanMemberForm
    else:
        return EditClanMemberForm


@clan_lead_view
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


@clan_lead_view
def list_members(request, clan):
    clan.sync_members()
    boxes = {}
    for member in clan.members.prefetch_related('box'):
        if member.box is not None and member.box.boxunit_set.count() > 0:
            boxes[member.id] = member.box.meta_json()
        else:
            boxes[member.id] = None
    ctx = {
        "clan": clan,
        "form": member_form(request, clan)(),
        "boxes": boxes
    }
    return render(request, 'rong/manageclan/members.html', ctx)
