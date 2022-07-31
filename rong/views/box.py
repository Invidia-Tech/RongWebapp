import base64
import json
import re
import zlib

from django.contrib import messages
from django.core.exceptions import SuspiciousOperation, BadRequest
from django.http import HttpRequest, Http404, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from rong.decorators import login_required
from rong.forms.box import EditBoxUnitForm, ImportTWArmoryBoxForm, CreateBoxUnitBulkForm, BoxForm, \
    ImportLoadIndexBoxForm
from rong.models import BoxUnit, Unit, Equipment, Box, Item


# views for box management

@login_required
def edit_inventory(request: HttpRequest, box_id):
    box = get_object_or_404(Box.full_data_queryset(), pk=box_id)
    if not box.can_edit(request.user):
        raise Http404('No box found.')
    items = Item.inventory_items()
    if request.method == 'POST':
        quantities = {}
        for item in items:
            item_key = "qty_%d" % item.id
            if item_key not in request.POST or not request.POST[item_key].isdigit():
                raise BadRequest()
            quantities[item.id] = int(request.POST[item_key])
        box.bulk_update_inventory(quantities)
        return JsonResponse({"success": True, "inventory": box.inventory_json(items)})
    return JsonResponse(box.inventory_json(items), safe=False)


@login_required
def edit_boxunit(request: HttpRequest, box_id, boxunit_id):
    box = get_object_or_404(Box.full_data_queryset(), pk=box_id)
    if not box.can_edit(request.user):
        raise Http404('No box found.')
    boxunit = get_object_or_404(box.boxunit_set, pk=boxunit_id)
    if request.method == 'POST':
        form = EditBoxUnitForm(request.POST, instance=boxunit)
        if form.is_valid():
            box.set_item_quantity(boxunit.unit.shard_id, form.cleaned_data["shards"])
            form.save()
            box.flag_updated()
            return JsonResponse({"success": True, "unit": boxunit.edit_json()})
        else:
            return JsonResponse({"success": False, "errors": form.errors.get_json_data()})
    elif request.method == 'DELETE':
        boxunit.delete()
        box.flag_updated()
        return JsonResponse({"success": True})
    elif request.method == 'GET':
        # return data needed to populate the unit editor
        return JsonResponse({"unit": boxunit.edit_json()})
    else:
        raise SuspiciousOperation()


@login_required
def import_loadindex(request: HttpRequest, box_id):
    box = get_object_or_404(Box.full_data_queryset(), pk=box_id)
    if not box.can_edit(request.user):
        raise Http404('No box found.')
    if request.method == 'POST':
        next = request.POST.get('next', '/')
        form = ImportLoadIndexBoxForm(request.POST)
        if form.is_valid():
            # process and error check the input
            try:
                data = json.loads(form.cleaned_data["data"].strip())
                assert type(data) == dict
                assert "data" in data or "unit_list" in data
                if "unit_list" not in data:
                    data = data["data"]
                assert type(data) == dict
                assert "unit_list" in data
                assert type(data["unit_list"]) == list
                for unit in data["unit_list"]:
                    assert type(unit) == dict
                    for field in ["id", "unit_rarity", "unit_level", "promotion_level"]:
                        assert field in unit
                        assert type(unit[field]) == int
                    for sfield in ["union_burst", "main_skill", "ex_skill", "free_skill"]:
                        assert sfield in unit
                        assert type(unit[sfield]) == list
                        for skill in unit[sfield]:
                            assert type(skill) == dict
                            assert "skill_level" in skill
                            assert type(skill["skill_level"]) == int
                            assert "skill_id" in skill
                            assert type(skill["skill_id"]) == int
                    for efield in ["equip_slot", "unique_equip_slot"]:
                        assert efield in unit
                        assert type(unit[efield]) == list
                        for equip in unit[efield]:
                            assert type(equip) == dict
                            for iefield in ["id", "is_slot", "enhancement_level"]:
                                assert iefield in equip
                                assert type(equip[iefield]) == int
                assert "item_list" in data
                assert type(data["item_list"]) == list
                for item in data["item_list"]:
                    assert type(item) == dict
                    for f in ["id", "stock"]:
                        assert f in item
                        assert type(item[f]) == int
            except Exception as ex:
                messages.add_message(request, messages.ERROR,
                                     "Could not import box data. Invalid /load/index data received.")
                return HttpResponseRedirect(next)
            # now the input looks ok, so start processing it according to the form choices
            try:
                save_units, new_units = box.import_loadindex(data)
            except ValueError as ex:
                messages.add_message(request, messages.ERROR, "Could not import box data. " + str(ex))
                return HttpResponseRedirect(next)
            messages.add_message(request, messages.SUCCESS,
                                 "Successfully imported %d units (%d new) from /load/index." % (
                                     save_units, new_units))
            return HttpResponseRedirect(next)
        else:
            messages.add_message(request, messages.ERROR, "Could not import box data. Form issue detected.")
            return HttpResponseRedirect(next)
    else:
        return render(request, 'rong/box/import_loadindex.html', {"form": ImportLoadIndexBoxForm(), "box": box})


@login_required
def import_box(request: HttpRequest, box_id):
    box = get_object_or_404(Box.full_data_queryset(), pk=box_id)
    if not box.can_edit(request.user):
        raise Http404('No box found.')
    if request.method == 'POST':
        next = request.POST.get('next', '/')
        form = ImportTWArmoryBoxForm(request.POST)
        if form.is_valid():
            # process and error check the input
            try:
                armory_import = json.loads(
                    zlib.decompress(base64.b64decode(form.cleaned_data["data"].strip()), 16 + zlib.MAX_WBITS).decode(
                        "UTF-8"))
                assert type(armory_import) == list
                assert len(armory_import) == 2 or len(armory_import) == 3
                units = armory_import[0]
                assert type(units) == list
                for unit in units:
                    assert type(unit) == dict
                    assert re.fullmatch(r"[01]{6}", unit["e"])
                    if type(unit["p"]) != int:
                        unit["p"] = int(unit["p"])
                    assert unit["p"] >= 1
                    if type(unit["r"]) != int:
                        unit["r"] = int(unit["r"])
                    assert 1 <= unit["r"] <= 6
                    unit["u"] = int(unit["u"], 16)
                    assert 1000 <= unit["u"] < 2000
                    if type(unit["t"]) != str:
                        unit["t"] = str(unit["t"]).lower()
                    assert re.fullmatch(r"(true|false|[1-9][0-9]*(\.[3-5])*)", unit["t"])
            except Exception as ex:
                messages.add_message(request, messages.ERROR,
                                     "Could not import box data. Invalid TW armory data received.")
                return HttpResponseRedirect(next)
            # now the input looks ok, so start processing it according to the form choices
            mode = form.cleaned_data["mode"]
            refines = form.cleaned_data["refines"]
            levels = form.cleaned_data["levels"]
            missing_units = form.cleaned_data["missing_units"]
            all_units = {u.id: u for u in Unit.valid_units().prefetch_related('ranks')}
            equipment_data = {eq.id: eq for eq in Equipment.objects.all()}
            save_units = []
            new_units = 0
            try:
                for unit in units:
                    uid = unit["u"] * 100 + 1
                    if uid in all_units:
                        unit_data = all_units[uid]
                        box_unit = box.boxunit_set.filter(unit_id=uid).first()
                        if not box_unit or mode != 'Append':
                            if not box_unit:
                                box_unit = BoxUnit(box=box, unit_id=uid, level=BoxUnit.max_level())
                                new_units += 1
                            if unit["p"] > unit_data.ranks.count():
                                raise ValueError(
                                    "You have %s's rank set to %d on Armory, which is beyond current EN ranks." % (
                                        unit_data.name, unit["p"]))
                            box_unit.rank = unit["p"]
                            box_unit.star = unit["r"]
                            if levels == 'Update to Max':
                                # TODO: skill levels
                                box_unit.level = BoxUnit.max_level()
                            if '.' in unit["t"] and int(unit["t"][:unit["t"].index(".")]) == unit["p"]:
                                # goal is rank x.3-5, update the equipment binary to turn off missing gear
                                goal_pieces = int(unit["t"][unit["t"].index(".") + 1:])
                                unit["e"] = list(unit["e"])
                                # topleft piece is always missing
                                unit["e"][0] = '0'
                                if goal_pieces < 5:
                                    # middleleft missing
                                    unit["e"][2] = '0'
                                if goal_pieces < 4:
                                    # bottomleft missing
                                    unit["e"][4] = '0'
                                unit["e"] = "".join(unit["e"])
                            current_rank = unit_data.ranks.all()[unit["p"] - 1]
                            for eq in range(6):
                                equip_on = unit["e"][eq] == '1'
                                if equip_on:
                                    eq_id = getattr(current_rank, "equip%d" % (eq + 1))
                                    if eq_id == 999999:
                                        raise ValueError(
                                            "You have a piece of gear equipped on %s that does not exist on EN yet." % unit_data.name)
                                    eq_val = equipment_data[eq_id].refine_stars if refines == 'Full' else 0
                                else:
                                    eq_val = None
                                setattr(box_unit, 'equip%d' % (eq + 1), eq_val)
                            box_unit.ue_level = int(unit["q"]) if unit["q"] != "" else None
                            save_units.append(box_unit)
                    elif missing_units == 'Error':
                        raise ValueError("Missing unit found in your import.")

                for box_unit in save_units:
                    box_unit.save()

                if mode == 'Overwrite':
                    box.boxunit_set.exclude(id__in=[bu.id for bu in save_units]).delete()
                box.flag_updated()
            except ValueError as ex:
                messages.add_message(request, messages.ERROR, "Could not import box data. " + str(ex))
                return HttpResponseRedirect(next)
            messages.add_message(request, messages.SUCCESS,
                                 "Successfully imported %d units (%d new) from TW Armory." % (
                                     len(save_units), new_units))
            return HttpResponseRedirect(next)
        else:
            messages.add_message(request, messages.ERROR, "Could not import box data. Form issue detected.")
            return HttpResponseRedirect(next)
    else:
        return render(request, 'rong/box/import_form.html', {"form": ImportTWArmoryBoxForm(), "box": box})


@login_required
def create_boxunit(request: HttpRequest, box_id):
    box = get_object_or_404(Box.full_data_queryset(), pk=box_id)
    if not box.can_edit(request.user):
        raise Http404('No box found.')
    if request.method == 'POST':
        form = CreateBoxUnitBulkForm(box, request.POST)
        if form.is_valid():
            results = [BoxUnit(box=box, unit=unit) for unit in form.cleaned_data["units"]]
            for result in results:
                result.save()
            box.flag_updated()
            return JsonResponse({"success": True, "units": [result.edit_json() for result in results]})
        else:
            return JsonResponse({"success": False, "errors": form.errors.get_json_data()})
    elif request.method == 'GET':
        return JsonResponse({"units": [{"id": u.id, "name": u.name, "range": u.search_area_width, "rarity": u.rarity}
                                       for u in box.missing_units().order_by('search_area_width')]})
    else:
        raise SuspiciousOperation()


@login_required
def edit_box(request: HttpRequest, box_id):
    box = get_object_or_404(Box.full_data_queryset(), pk=box_id)
    if not box.can_edit(request.user):
        raise Http404('No box found.')
    if hasattr(box, "clanmember"):
        raise SuspiciousOperation()
    if request.method == 'POST':
        form = BoxForm(request.user, request.POST, instance=box)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "box": box.as_json()})
        else:
            return JsonResponse({"success": False, "error": "Invalid box"})
    elif request.method == 'DELETE':
        box.delete()
        return JsonResponse({"success": True})
    elif request.method == 'GET':
        return JsonResponse({"name": box.name})
    else:
        raise SuspiciousOperation()


@login_required
def create_box(request: HttpRequest):
    if request.method == 'POST':
        form = BoxForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "box": form.instance.as_json()})
        else:
            return JsonResponse({"success": False, "error": "Invalid box"})
    else:
        raise SuspiciousOperation()


@login_required
def index(request: HttpRequest):
    boxes = [box.as_json() for box in request.user.boxes.all()]
    return render(request, 'rong/box/index.html', {"boxes": boxes})
