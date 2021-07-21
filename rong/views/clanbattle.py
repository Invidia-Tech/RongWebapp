import json
from collections import defaultdict

from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from rong.decorators import clan_view, clanbattle_view, clanbattle_lead_view
from rong.forms.clanbattle import HitForm
from rong.models import ClanBattle
from rong.models.clan_battle_score import ClanBattleHitType, ClanBattleScore


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
    hits = list(battle.hits.select_related('user', 'team', 'team__unit1', 'team__unit2', 'team__unit3', 'team__unit4',
                                           'team__unit5').order_by('order'))
    daily_attempt_counts = defaultdict(lambda: 0)
    day = None
    for hit in hits:
        if hit.day != day:
            daily_attempt_counts.clear()
            day = hit.day
        hit.attempt_count = daily_attempt_counts[hit.user_id] + (1 if hit.hit_type == ClanBattleHitType.NORMAL else 0.5)
        daily_attempt_counts[hit.user_id] = hit.attempt_count
    ctx = {
        'battle': battle,
        'hits': hits,
        'hits_per_day': ClanBattle.HITS_PER_DAY
    }
    return render(request, 'rong/clanbattle/hit_log.html', ctx)


@clanbattle_view
def view_battle(request, battle: ClanBattle):
    ctx = {
        'in_clan': request.user.in_clan(battle.clan),
        'battle': battle,
        'hits': battle.hits.select_related('user').order_by('-order')[:30],
        'myhits': battle.hits.filter(user=request.user).order_by('-order')[:30],
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
