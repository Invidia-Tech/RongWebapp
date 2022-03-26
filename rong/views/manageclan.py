from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from rong.decorators import clan_lead_view, clan_admin_view, clan_boxes_view
from rong.forms.manageclan import HitGroupForm, EditClanBattleForm, AddClanBattleForm, FullEditClanMemberForm, \
    EditClanMemberForm, HitTagForm, ClanBattleCompForm
from rong.models import ClanBattle, HitGroup, HitTag, User, ClanMember, ClanBattleComp

@clan_lead_view
def edit_comp(request, clan, battle_id, comp_id):
    battle = get_object_or_404(clan.clanbattle_set, pk=battle_id)
    comp = get_object_or_404(battle.comps, pk=comp_id)
    if request.method == 'POST':
        form = ClanBattleCompForm(comp, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Comp successfully edited.")
        return redirect(
            reverse('rong:clan_edit_battle', kwargs={'clan': clan.slug, 'battle_id': battle.id}) + '#comps')
    elif request.method == 'DELETE':
        comp.delete()
        messages.add_message(request, messages.SUCCESS, "Comp successfully deleted.")
        return JsonResponse({'success': True})
    else:
        form = ClanBattleCompForm(comp)
    ctx = {
        'form': form,
        'clan': clan,
        'battle': battle,
        'comp': comp
    }
    return render(request, 'rong/manageclan/edit_comp.html', ctx)


@clan_lead_view
def add_comp(request, clan, battle_id):
    battle = get_object_or_404(clan.clanbattle_set, pk=battle_id)
    if request.method == 'POST':
        form = ClanBattleCompForm(ClanBattleComp(clan_battle=battle, submitter=request.user), request.POST, prefix="add-comp")
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Successfully added new comp.")
        else:
            messages.add_message(request, messages.ERROR, "Could not add new comp.")
        return redirect(
            reverse('rong:clan_edit_battle', kwargs={'clan': clan.slug, 'battle_id': battle.id}) + '#comps')
    else:
        raise SuspiciousOperation()


@clan_lead_view
def edit_hit_group(request, clan, battle_id, group_id):
    battle = get_object_or_404(clan.clanbattle_set, pk=battle_id)
    group = get_object_or_404(battle.hit_groups, pk=group_id)
    if request.method == 'POST':
        form = HitGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Hit Group successfully edited.")
        return redirect(
            reverse('rong:clan_edit_battle', kwargs={'clan': clan.slug, 'battle_id': battle.id}) + '#hit-groups')
    elif request.method == 'DELETE':
        if group.hits.count():
            return JsonResponse({'success': False, 'error': 'Cannot delete hit group with tagged hits.'})
        else:
            group.delete()
            messages.add_message(request, messages.SUCCESS, "Hit Group successfully deleted.")
            return JsonResponse({'success': True})
    else:
        form = HitGroupForm(instance=group)
    ctx = {
        'form': form,
        'clan': clan,
        'battle': battle,
        'group': group,
    }
    return render(request, 'rong/manageclan/edit_hit_group.html', ctx)


@clan_lead_view
def add_hit_group(request, clan, battle_id):
    battle = get_object_or_404(clan.clanbattle_set, pk=battle_id)
    if request.method == 'POST':
        form = HitGroupForm(request.POST, prefix="add-group", instance=HitGroup(clan_battle=battle))
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Successfully added new hit group.")
        else:
            messages.add_message(request, messages.ERROR, "Could not add new hit group.")
        return redirect(
            reverse('rong:clan_edit_battle', kwargs={'clan': clan.slug, 'battle_id': battle.id}) + '#hit-groups')
    else:
        raise SuspiciousOperation()


@clan_lead_view
def edit_hit_tag(request, clan, tag_id):
    tag = get_object_or_404(clan.hit_tags, pk=tag_id)
    if request.method == 'POST':
        form = HitTagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Tag successfully edited.")
            return redirect('rong:clan_list_hit_tags')
    else:
        form = HitTagForm(instance=tag)
    ctx = {
        'form': form,
        'clan': clan,
        'tag': tag,
    }
    return render(request, 'rong/manageclan/edit_tag.html', ctx)


@clan_lead_view
def add_hit_tag(request, clan):
    if request.method == 'POST':
        tag = HitTag(clan=clan)
        form = HitTagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Tag successfully added.")
            return redirect('rong:clan_list_hit_tags', clan.slug)
    else:
        form = HitTagForm()
    ctx = {
        'form': form,
        'clan': clan
    }
    return render(request, 'rong/manageclan/add_tag.html', ctx)


@clan_lead_view
def list_hit_tags(request, clan):
    ctx = {
        "clan": clan,
    }
    return render(request, 'rong/manageclan/tags.html', ctx)


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
    else:
        form = EditClanBattleForm(instance=battle)
    ctx = {
        'detailsform': form,
        'clan': clan,
        'battle': battle,
        'hgform': HitGroupForm(prefix="add-group"),
        'compform': ClanBattleCompForm(comp=ClanBattleComp(clan_battle=battle), prefix="add-comp"),
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


@clan_admin_view
def add_member(request, clan):
    form_class = member_form(request, clan)
    if request.method == 'POST':
        member = ClanMember(clan=clan)
        form = form_class(request.POST, instance=member)
        if form.is_valid():
            member.user = User.for_discord_id(form.cleaned_data["discord"])
            form.save()
            return JsonResponse({"success": True, "member": member.json})
        else:
            return JsonResponse({"success": False, "error": "Invalid member"})
    else:
        raise SuspiciousOperation()


@clan_lead_view
def edit_member(request, clan, member_id):
    member = get_object_or_404(clan.all_members, pk=member_id)
    form_class = member_form(request, clan)
    if request.method == 'POST':
        form = form_class(request.POST, instance=member)
        if form.is_valid():
            member.user = User.for_discord_id(form.cleaned_data["discord"])
            form.save()
            return JsonResponse({"success": True, "member": member.json})
        else:
            return JsonResponse({"success": False, "error": "Invalid member"})
    elif request.method == 'GET':
        return JsonResponse(member.json)
    else:
        raise SuspiciousOperation()


@clan_boxes_view
def box_summary(request, clan):
    member_data = clan.members.select_related('box', 'user').prefetch_related('box__boxunit_set__unit__ranks',
                                                                              'box__boxunit_set__unit__unique_equip',
                                                                              'box__inventory')
    members = [member.as_json(True) for member in member_data]
    seen_units = []
    units = []
    for member in members:
        for buid in member["box"]["units"]:
            bunit = member["box"]["units"][buid]
            if bunit["unit"]["id"] not in seen_units:
                bunit["unit"]["ranks"] = bunit["ranks"]
                seen_units.append(bunit["unit"]["id"])
                units.append(bunit["unit"])
            bunit["unit_id"] = bunit["unit"]["id"]
            del bunit["unit"]
            del bunit["ranks"]
    units.sort(key=lambda x: x["name"])
    ctx = {
        "clan": clan,
        "members": members,
        "units": units,
    }
    return render(request, 'rong/manageclan/box_summary.html', ctx)


@clan_lead_view
def list_members(request, clan):
    boxes = {}
    members = clan.all_members.select_related('box', 'user').prefetch_related('box__boxunit_set__unit__ranks',
                                                                              'box__boxunit_set__unit__unique_equip',
                                                                              'box__inventory')
    active_members = []
    inactive_members = []
    for member in members:
        if member.box is None:
            member.save()  # create a box
        boxes[member.id] = member.box.as_json()
        if member.active:
            active_members.append(member)
        else:
            inactive_members.append(member)
    ctx = {
        "clan": clan,
        "active_members": active_members,
        "inactive_members": inactive_members,
        "form": member_form(request, clan)(),
        "boxes": boxes,
        "show_add": request.user.can_administrate(clan)
    }
    return render(request, 'rong/manageclan/members.html', ctx)
