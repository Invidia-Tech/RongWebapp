import datetime
import json
import traceback

import pytz
from django.conf import settings
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
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
        if not clan.nearest_cb:
            return JsonResponse({"success": False, "error": "No active CB"})
        if clan.nearest_cb.start_time > timezone.now():
            return JsonResponse({"success": False, "error": "CB %s has not started yet" % clan.nearest_cb.name})
        if clan.nearest_cb.end_time + datetime.timedelta(days=3) < timezone.now():
            return JsonResponse({"success": False, "error": "CB %s ended more than 3 days ago" % clan.nearest_cb.name})
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
        hit.clan_battle = clan.nearest_cb
        hit.member = hitter
        hit.day = min(clan.nearest_cb.current_day, clan.nearest_cb.total_days)
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
        num_players = ClanMember.objects.filter(player_id=data["viewer_id"], active=True, out_of_clan=False).count()
        if not num_players:
            return JsonResponse({"success": False, "error": "No active players found matching provided viewer id"})
        if num_players > 1:
            return JsonResponse(
                {"success": False, "error": "Multiple active players found matching provided viewer id"})
        player = ClanMember.objects.get(player_id=data["viewer_id"], active=True, out_of_clan=False)
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
        active_flights = Flight.objects.filter(status="in flight").select_related("passenger", "pilot")
        for flight in active_flights:
            if flight.passenger:
                if flight.passenger.active and flight.passenger.player_id in statuses:
                    statuses[flight.passenger.player_id] = True
            else:
                if flight.pilot.clanmember and flight.pilot.clanmember.player_id in statuses:
                    statuses[flight.pilot.clanmember.player_id] = True
        return JsonResponse({"statuses": statuses})
    except Exception as ex:
        return JsonResponse(
            {"error": "Exception thrown when handling request, probably malformed", "error_detail": str(ex),
             "traceback": str(traceback.format_exc())})


@csrf_exempt
def gearbot_fc_check(request):
    try:
        if request.method != "POST" or "X-Gearbot-Memez" not in request.headers:
            return JsonResponse({"boo": "PUDDING DAYO"})
        data = json.loads(request.body)
        statuses = {viewer_id: False for viewer_id in data["viewer_ids"]}
        for clan in Clan.objects.all():
            if clan.current_cb and clan.current_cb.in_progress:
                for fc in clan.current_cb.forcequits.filter(day=clan.current_cb.current_day).select_related(
                        'clanmember'):
                    if fc.clanmember.active and fc.clanmember.player_id in statuses:
                        statuses[fc.clanmember.player_id] = True
        return JsonResponse({"statuses": statuses})
    except Exception as ex:
        return JsonResponse(
            {"error": "Exception thrown when handling request, probably malformed", "error_detail": str(ex),
             "traceback": str(traceback.format_exc())})


@csrf_exempt
def gearbot_add_hits(request):
    try:
        if request.method != "POST" or "X-Gearbot-Memez" not in request.headers:
            return JsonResponse({"boo": "PUDDING DAYO"})
        data = json.loads(request.body)
        clan = Clan.objects.filter(name__iexact=data['clan']).first()
        if not clan:
            return JsonResponse({"success": False, "error": "Invalid clan"})
        if not clan.nearest_cb:
            return JsonResponse({"success": False, "error": "No active CB"})
        if clan.nearest_cb.start_time > timezone.now():
            return JsonResponse({"success": False, "error": "CB %s has not started yet" % clan.nearest_cb.name})
        if clan.nearest_cb.end_time + datetime.timedelta(days=3) < timezone.now():
            return JsonResponse({"success": False, "error": "CB %s ended more than 3 days ago" % clan.nearest_cb.name})
        if not data["hits"]:
            return JsonResponse({"success": True, "created_hits": 0})
        existing_hits = clan.nearest_cb.hits.filter(
            ingame_log_id__in=[hit["log"]["history_id"] for hit in data["hits"]]).values_list('ingame_log_id',
                                                                                              flat=True)
        all_units = {unit.id: unit for unit in Unit.valid_units()}
        hits = list(data["hits"])
        hits.sort(key=lambda x: x["log"]["create_time"])
        created_hits = []
        for hit_data in hits:
            log = hit_data["log"]
            report = hit_data["report"]
            if log["history_id"] in existing_hits:
                continue
            hitter = clan.in_clan_members.filter(player_id=log["viewer_id"]).first()
            if not hitter:
                return JsonResponse(
                    {"success": False, "error": "No active in-clan member with player id %d" % log["viewer_id"]})
            units = []
            damages = []
            for unit in report["history_report"]:
                if unit["viewer_id"] == 0:
                    # boss
                    continue
                else:
                    units.append(all_units[unit["unit_id"]])
                    damages.append(unit["damage"])
            # create hit
            hit = ClanBattleScore()
            hit.ingame_log_id = log["history_id"]
            hit.ingame_timestamp = datetime.datetime.fromtimestamp(log["create_time"],
                                                                   pytz.timezone(settings.TIME_ZONE))
            hit.ingame_fulldata = json.dumps(hit_data)
            hit.clan_battle = clan.nearest_cb
            hit.member = hitter
            hit.day = clan.nearest_cb.day_of(hit.ingame_timestamp)
            hit.damage = log["damage"]
            team, ordering = create_team(units)
            hit.team = team
            for idx, dmg in enumerate(damages):
                new_idx = ordering.index(idx)
                setattr(hit, "unit%d_damage" % (new_idx + 1), dmg)
            for i in range(len(damages), 5):
                setattr(hit, "unit%d_damage" % (i + 1), None)
            hit.ign = hitter.ign
            # attempt to automatch pilot with ATC
            matching_flights = hit.clan_battle.flights.filter(models.Q(start_time__lte=hit.ingame_timestamp) & (
                    models.Q(end_time=None) | models.Q(end_time__gte=hit.ingame_timestamp)) & models.Q(
                status__in=["in flight", "landed"]) & models.Q(passenger=hitter)).select_related('pilot')
            if len(matching_flights) == 1:
                hit.pilot = matching_flights[0].pilot.clanmember
            created_hits.append(hit)
        # should be good to save hits if we got this far
        for hit in created_hits:
            hit.save()
        # integrity check
        if created_hits:
            clan.nearest_cb.recalculate()
        return JsonResponse({"success": True, "created_hits": len(created_hits)})

    except Exception as ex:
        return JsonResponse({"success": False, "error": "Exception thrown when handling request, probably malformed",
                             "error_detail": str(ex), "traceback": str(traceback.format_exc())})
