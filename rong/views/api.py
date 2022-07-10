import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rong.models import Unit, Clan, UnitAlias, ClanMember, Flight
from rong.models.clan_battle_score import ClanBattleScore
from rong.models.team import create_team


@csrf_exempt
def kyaru_add_hit(request):
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
        all_units = {unit.id: unit for unit in Unit.valid_units()}
        aliases = {}
        for al in UnitAlias.objects.all():
            if al.unit_id in all_units:
                aliases[al.name.lower()] = all_units[al.unit_id]
        aliases.update({unit.name.lower(): unit for unit in all_units.values()})
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
        if "comp" in data:
            comp = clan.comps.filter(name__iexact=data['comp']).first()
            if comp:
                hit.comp = comp
                hit.comp_locked = True
        hit.save()
        return JsonResponse({"success": True})

    except Exception as ex:
        return JsonResponse({"success": False, "error": "Exception thrown when handling request, probably malformed"})


@csrf_exempt
def gearbot_update_box(request):
    try:
        if request.method != "POST" or "X-Gearbot-Memez" not in request.headers:
            return JsonResponse({"boo": "PUDDING DAYO"})
        data = json.loads(request.body)
        num_players = ClanMember.objects.filter(player_id=data["viewer_id"], active=True).count()
        if not num_players:
            return JsonResponse(
                {"success": False, "error": "No active players found matching provided viewer id"})
        if num_players > 1:
            return JsonResponse(
                {"success": False, "error": "Multiple active players found matching provided viewer id"})
        player = ClanMember.objects.get(player_id=data["viewer_id"], active=True)
        player.box.import_loadindex(data["load_index"])
        return JsonResponse({"success": True})

    except Exception as ex:
        return JsonResponse({"success": False, "error": "Exception thrown when handling request, probably malformed"})


@csrf_exempt
def gearbot_flight_check(request):
    try:
        if request.method != "POST" or "X-Gearbot-Memez" not in request.headers:
            return JsonResponse({"boo": "PUDDING DAYO"})
        data = json.loads(request.body)
        statuses = {viewer_id: False for viewer_id in data["viewer_ids"]}
        flights = Flight.objects.filter(passenger__player_id__in=data["viewer_ids"], passenger__active=True,
                                        status="in flight").select_related("passenger")
        for flight in flights:
            statuses[flight.passenger.player_id] = True
        return JsonResponse({"statuses": statuses})
    except Exception as ex:
        return JsonResponse({"error": "Exception thrown when handling request, probably malformed"})
