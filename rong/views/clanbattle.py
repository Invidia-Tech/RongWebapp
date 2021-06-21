import json
from collections import defaultdict

from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.db import transaction
from django.shortcuts import render

from rong.decorators import clan_view, clanbattle_view
# Create your views here.
from rong.models import ClanBattle
from rong.models.clan_battle_score import ClanBattleHitType


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
            with transaction.atomic():
                for hit in reordered_hits:
                    hit.order = int(reorder_data[str(hit.id)])
                    hit.save()
                battle.recalculate()
            messages.add_message(request, messages.SUCCESS, "Hits successfully reordered.")
        except Exception:
            raise SuspiciousOperation()
    hits = list(battle.hits.select_related('user', 'team').order_by('order'))
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
    ctx = {
        'in_clan': request.user.in_clan(clan),
        'clan': clan
    }
    return render(request, 'rong/clanbattle/list.html', ctx)
