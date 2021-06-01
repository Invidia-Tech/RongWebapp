from rong.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest
from rong.forms import BoxForm, CreateBoxUnitForm, EditBoxUnitForm
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.shortcuts import get_object_or_404
from rong.models import BoxUnit
from django.http import JsonResponse

# views for box management


@login_required
def alter_boxunit(request: HttpRequest, box_id, boxunit_id):
    box = get_object_or_404(request.user.box_set, pk=box_id)
    boxunit = get_object_or_404(box.boxunit_set, pk=boxunit_id)
    if request.method == 'POST':
        form = EditBoxUnitForm(request.POST, instance=boxunit)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "unit": boxunit.edit_json()})
        else:
            return JsonResponse({"success": False, "errors": form.errors.get_json_data()})
    elif request.method == 'DELETE':
        boxunit.delete()
        return JsonResponse({"success": True})
    elif request.method == 'GET':
        # return data needed to populate the unit editor
        return JsonResponse({"unit": boxunit.edit_json()})
    else:
        raise SuspiciousOperation()


@login_required
def create_boxunit(request: HttpRequest, box_id):
    box = get_object_or_404(request.user.box_set, pk=box_id)
    if request.method == 'POST':
        box_unit = BoxUnit(box=box)
        form = CreateBoxUnitForm(request.POST, instance=box_unit)
        if form.is_valid():
            # because box isn't part of the form, we have to validate uniqueness ourselves
            try:
                box_unit.validate_unique()
                form.save()
                return JsonResponse({"success": True, "unit": box_unit.edit_json()})
            except ValidationError as ex:
                return JsonResponse({"success": False, "errors": [str(ex)]})
        else:
            return JsonResponse({"success": False, "errors": form.errors.get_json_data()})
    elif request.method == 'GET':
        return JsonResponse({"units": [{"id": u.id, "name": u.name, "range": u.search_area_width, "rarity": u.rarity} for u in box.missing_units().order_by('search_area_width')]})
    else:
        raise SuspiciousOperation()


@login_required
def alter_box(request: HttpRequest, box_id):
    if request.user.single_mode:
        raise SuspiciousOperation("Trying to edit/delete box in single mode")
    box = get_object_or_404(request.user.box_set, pk=box_id)
    if request.method == 'POST':
        form = BoxForm(request.user, request.POST, instance=box)
        if form.is_valid():
            form.save()
            # clan change? must be done manually
            clanUnchanged = hasattr(box, 'clanmember') and form.data.get(
                "clan", "") and int(form.data["clan"]) == int(box.clanmember.id)
            if hasattr(box, 'clanmember') and not clanUnchanged:
                # clear old clan
                cm = box.clanmember
                cm.box = None
                cm.save()
            if form.data.get("clan", "") and not clanUnchanged:
                # set new clan
                cm = request.user.clanmember_set.get(pk=form.data["clan"])
                cm.box = box
                cm.save()
            return JsonResponse({"success": True, "box": box.meta_json()})
        else:
            return JsonResponse({"success": False, "error": "Invalid box"})
    elif request.method == 'DELETE':
        box.delete()
        return JsonResponse({"success": True})
    elif request.method == 'GET':
        form = BoxForm(request.user, instance=box)
        return JsonResponse({"name": box.name, "clan": box.clanmember.id if hasattr(box, 'clanmember') else None, "clan_options": [(cm.id, str(cm)) for cm in form.fields["clan"].queryset]})
    else:
        raise SuspiciousOperation()


@login_required
def create_box(request: HttpRequest):
    if request.user.single_mode:
        raise SuspiciousOperation("Trying to create box in single mode")
    if request.method == 'POST':
        form = BoxForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # clan?
            if "clan" in form.data and form.data["clan"]:
                cm = request.user.clanmember_set.get(pk=form.data["clan"])
                cm.box = form.instance
                cm.save()
            return JsonResponse({"success": True, "box": form.instance.meta_json()})
        else:
            return JsonResponse({"success": False, "error": "Invalid box"})
    elif request.method == 'GET':
        form = BoxForm(request.user)
        return JsonResponse({"clan_options": [(cm.id, str(cm)) for cm in form.fields["clan"].queryset]})
    else:
        raise SuspiciousOperation()


@login_required
def index(request: HttpRequest):
    request.user.check_single_mode()
    boxes = [box.meta_json() for box in request.user.box_set.all()]
    return render(request, 'rong/box/index.html', {"boxes": boxes})
