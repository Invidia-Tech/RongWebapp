import json
import traceback
from collections import defaultdict

from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from rong.decorators import clan_view, clanbattle_view, clanbattle_lead_view
from rong.forms.clanbattle import HitForm
from rong.models import ClanBattle, Unit, Clan, UnitAlias
from rong.models.clan_battle_score import ClanBattleHitType, ClanBattleScore
from rong.models.team import create_team
from rong.templatetags.clan_battle import format_hits

@csrf_exempt
def add_hit(request):
    try:
        if request.method != "POST" or "X-Kyaru-Bot" not in request.headers:
            return JsonResponse({"boo": "PUDDING DAYO"})
        data = json.loads(request.body)
        clan = Clan.objects.filter(name__iexact=data['clan']).first()
        if not clan:
            return JsonResponse({"success": False, "error": "Invalid clan"})
        if not clan.current_cb or not clan.current_cb.in_progress:
            return JsonResponse({"success": False, "error": "No active CB"})
        hitter = clan.members.filter(ign__iexact=data['account']).first()
        if not hitter:
            return JsonResponse({"success": False, "error": "Could not find account"})
        if len(data["units"]) != len(data["damages"]):
            return JsonResponse({"success": False, "error": "Missing or extra damages"})
        all_units = {unit.id:unit for unit in Unit.objects.all()}
        aliases = {al.name.lower():all_units[al.unit_id] for al in UnitAlias.objects.all()}
        aliases.update({unit.name.lower():unit for unit in all_units.values()})
        valid_units = []
        invalid_units = []
        duplicate_units = []
        for unit_name in data["units"]:
            if unit_name.lower() not in aliases:
                invalid_units.append(unit_name)
            elif aliases[unit_name.lower()] in valid_units:
                duplicate_units.append(unit_name)
            else:
                valid_units.append(aliases[unit_name.lower()])
        if invalid_units:
            return JsonResponse({"success": False, "error": "Unknown units: %s" % str(invalid_units)})
        if duplicate_units:
            return JsonResponse({"success": False, "error": "Duplicate units: %s" % str(duplicate_units)})
        # create hit
        hit = ClanBattleScore()
        hit.clan_battle = clan.current_cb
        hit.member = hitter
        hit.day = clan.current_cb.current_day
        hit.damage = int(data["total_damage"])
        hit.kyaru_date = data["date"]
        hit.kyaru_author = data["author"]
        hit.kyaru_image_url = data["image_url"]
        hit.kyaru_boss_number = int(data["stage"])
        team, ordering = create_team(valid_units)
        hit.team = team
        for idx, dmg in enumerate(data["damages"]):
            new_idx = ordering.index(idx)
            setattr(hit, "unit%d_damage" % (new_idx + 1), dmg)
        for i in range(len(data["damages"]), 5):
            setattr(hit, "unit%d_damage" % (i + 1), None)
        hit.ign = hitter.ign
        if "pilot" in data:
            hit.kyaru_pilot = data["pilot"]
            hit.pilot = clan.members.filter(ign__iexact=data['pilot']).first()
        hit.save()
        return JsonResponse({"success": True})

    except Exception as ex:
        return JsonResponse({"success": False, "error": "Exception thrown when handling request, probably malformed"})


