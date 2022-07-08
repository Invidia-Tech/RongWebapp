import json
from collections import defaultdict

from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from rong.decorators import clan_view, clanbattle_view, clanbattle_lead_view
from rong.forms.clanbattle import HitForm
from rong.models import ClanBattle, Unit
from rong.models.clan_battle_score import ClanBattleHitType, ClanBattleScore
from rong.templatetags.clan_battle import format_hits


@clanbattle_lead_view
def edit_hit(request, battle: ClanBattle, hit_id):
    hit = get_object_or_404(battle.hits, pk=hit_id)
    if request.method == 'DELETE':
        order_val = hit.order
        hit.delete()
        battle.hits.filter(order__gt=order_val).update(order=F('order') - 1)
        battle.recalculate()
        messages.add_message(request, messages.SUCCESS, 'Hit successfully deleted.')
        return JsonResponse({'success': True})
    elif request.method == 'POST':
        form = HitForm(hit, data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Hit successfully edited.')
            return redirect('rong:cb_list_hits', battle.slug)
    else:
        form = HitForm(hit)
    ctx = {
        'battle': battle,
        'form': form,
    }
    return render(request, 'rong/clanbattle/edit_hit.html', ctx)


@clanbattle_lead_view
def add_hit(request, battle: ClanBattle):
    if request.method == 'POST':
        form = HitForm(ClanBattleScore(clan_battle=battle), data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Hit successfully added.')
            return redirect('rong:cb_list_hits', battle.slug)
    else:
        form = HitForm(ClanBattleScore(clan_battle=battle))
    ctx = {
        'battle': battle,
        'form': form,
    }
    return render(request, 'rong/clanbattle/add_hit.html', ctx)


@clanbattle_view
def hit_log_data(request, battle: ClanBattle):
    hits = list(battle.hits.select_related('member', 'member__user', 'team', 'team__unit1', 'team__unit2', 'team__unit3', 'team__unit4',
                                           'team__unit5', 'group', 'comp', 'pilot', 'pilot__user').prefetch_related('tags').order_by('order'))
    daily_attempt_counts = defaultdict(lambda: 0)
    day = None
    hits_json = []
    manageable = request.user.can_manage(battle)
    tags = set()
    groups = set()
    members = set()
    comps = set()
    boss_codes = set()
    pilots = set()
    players = set()
    boss_data = list(battle.bosses.order_by('difficulty').all())
    member_list = list(battle.clan.members.select_related('user'))
    pilot_choices = [(x.id, x.ign) for x in member_list]
    phase = 1
    for hit in hits:
        if boss_data[phase-1].lap_to is not None and hit.boss_lap > boss_data[phase-1].lap_to:
            phase += 1
        if hit.day != day:
            daily_attempt_counts.clear()
            day = hit.day
        hit.attempt_count = daily_attempt_counts[hit.member_id] + (1 if hit.hit_type == ClanBattleHitType.NORMAL else 0.5)
        daily_attempt_counts[hit.member_id] = hit.attempt_count
        hit_json = {
            "order": hit.order,
            "day": hit.day,
            "username": hit.displayed_username,
            "pilot": hit.displayed_pilot,
            "team": hit.team.units if hit.team else False,
            "damage": {
                "damage": hit.damage,
                "actual": hit.actual_damage,
            },
            "lap": hit.boss_lap,
            "boss": {
                "number": hit.boss_number,
                "icon": getattr(battle, 'boss%d_iconid' % hit.boss_number),
                "name": getattr(battle, 'boss%d_name' % hit.boss_number),
            },
            "hp_left": hit.boss_hp_left,
            "attempts": {
                "value": format_hits(hit.attempt_count),
                "per_day": ClanBattle.HITS_PER_DAY,
            },
            "hit_type": hit.hit_type.value,
            "phase": phase,
            "comp": "None" if hit.comp is None else hit.comp.name,
            "boss_code": chr(0x40 + phase)+str(hit.boss_number),
        }
        if manageable:
            hit_json["id"] = hit.id
            hit_json["member_id"] = hit.member_id
            hit_json["player_id"] = hit.pilot_id if hit.pilot_id else hit.member_id
            hit_json["pilot_id"] = hit.pilot_id if hit.pilot_id else 0
            hit_json["links"] = {
                "edit_url": reverse('rong:cb_edit_hit', args=[battle.slug, hit.id])
            }
            hit_json["group"] = hit.group.id if hit.group else None
            hit_json["tags"] = [tag.id for tag in hit.tags.all()]
            members.add(hit.member)
            if hit.group:
                groups.add(hit.group)
            if hit.pilot:
                pilots.add(hit.pilot)
                players.add(hit.pilot)
            else:
                players.add(hit.member)
            tags.update(hit.tags.all())
            comps.add(hit_json["comp"])
            boss_codes.add(hit_json["boss_code"])
            if hit.pilot_id and hit.pilot_id not in [x[0] for x in pilot_choices]:
                pilot_choices.append((hit.pilot_id, hit.pilot.ign))
            if hit.member_id and hit.member_id not in [x[0] for x in pilot_choices]:
                pilot_choices.append((hit.member_id, hit.member.ign))
        hits_json.append(hit_json)
    resp = {
        "hits": hits_json
    }
    if manageable:
        resp["tags"] = [(tag.id,tag.name) for tag in tags]
        resp["groups"] = [(group.id,group.name) for group in groups]
        resp["unit_choices"] = [(unit.id,unit.name) for unit in Unit.valid_units().order_by('search_area_width')]
        resp["members"] = [(member.id,member.ign) for member in members]
        resp["boss_choices"] = [(num, getattr(battle, "boss%d_name" % num)) for num in range(1, 6)]
        resp["players"] = [(member.id, member.ign) for member in players]
        resp["pilots"] = [(member.id, member.ign) for member in pilots]
        resp["members"].sort(key=lambda x:x[1].lower())
        resp["players"].sort(key=lambda x: x[1].lower())
        resp["pilots"].sort(key=lambda x: x[1].lower())
        resp["pilots"] = [(0, "Self Hit")] + resp["pilots"]
        resp["unit_choices"].sort(key=lambda x: x[1].lower())
        resp["comps"] = [(c, c) for c in comps]
        resp["comps"].sort(key=lambda x:x[1].lower())
        resp["boss_codes"] = [(c, c) for c in boss_codes]
        resp["boss_codes"].sort(key=lambda x:x[1].lower())
        resp["pilot_choices"] = pilot_choices
        resp["pilot_choices"].sort(key=lambda x:x[1].lower())
        resp["pilot_choices"] = [(0, "Self Hit")] + resp["pilot_choices"]
    return JsonResponse(resp)


@clanbattle_view
def hit_log(request, battle: ClanBattle):
    if request.method == 'POST':
        try:
            reorder_data = json.loads(request.POST['reorderData'])
            assert isinstance(reorder_data, dict)
            assert len(reorder_data)
            reordered_hits = list(battle.hits.filter(pk__in=[int(n) for n in reorder_data.keys()]))
            assert len(reordered_hits) == len(reorder_data)
            assert set(hit.order for hit in reordered_hits) == set(int(n) for n in reorder_data.values())
            reordered_hits.sort(key=lambda hit: int(reorder_data[str(hit.id)]))
            last_day = 0
            day_ok = True
            for hit in reordered_hits:
                if hit.day < last_day:
                    day_ok = False
                    break
                last_day = hit.day
            if day_ok:
                with transaction.atomic():
                    for hit in reordered_hits:
                        hit.order = int(reorder_data[str(hit.id)])
                        hit.save()
                    battle.recalculate()
                messages.add_message(request, messages.SUCCESS, "Hits successfully reordered.")
            else:
                messages.add_message(request, messages.ERROR,
                                     "You can't reorder hits that would mess up the day order. Please edit the hits to change the day instead.")
        except Exception:
            messages.add_message(request, messages.ERROR, "Could not reorder hits.")
    ctx = {
        'battle': battle
    }
    return render(request, 'rong/clanbattle/hit_log.html', ctx)


@clanbattle_view
def view_battle(request, battle: ClanBattle):
    ctx = {
        'in_clan': request.user.in_clan(battle.clan),
        'battle': battle,
        'hits': list(battle.hits.select_related('member', 'member__user').order_by('-order'))[:30],
        'myhits': list(battle.hits.filter(member__user=request.user).order_by('-order'))[:30],
    }
    return render(request, 'rong/clanbattle/view.html', ctx)


@clan_view
def list_battles(request, clan):
    # do something
    request.user.preload_perms()
    ctx = {
        'in_clan': request.user.in_clan(clan),
        'clan': clan,
        'current_cb': clan.current_cb if clan.current_cb and request.user.can_view(clan.current_cb) else None,
        'future_cbs': [cb for cb in clan.future_cbs if request.user.can_view(cb)],
        'past_cbs': [cb for cb in clan.past_cbs if request.user.can_view(cb)],
    }
    return render(request, 'rong/clanbattle/list.html', ctx)
