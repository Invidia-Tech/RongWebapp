from rong.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from rong.forms import BoxForm, CreateBoxUnitForm, EditBoxUnitForm
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.shortcuts import get_object_or_404
from rong.models import BoxUnit
from django.http import JsonResponse

# views for box management

@login_required
def alter_boxunit(request : HttpRequest, box_id, boxunit_id):
    box = get_object_or_404(request.user.box_set, pk=box_id)
    boxunit = get_object_or_404(box.boxunit_set, pk=boxunit_id)
    if request.method == 'POST':
        form = EditBoxUnitForm(request.POST, instance=boxunit)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors.get_json_data()})
    elif request.method == 'DELETE':
        boxunit.delete()
        return JsonResponse({"success": True})
    elif request.method == 'GET':
        # TODO return data needed to populate the unit editor
        return JsonResponse({"wip": True})
    else:
        raise SuspiciousOperation()

@login_required
def create_boxunit(request : HttpRequest, box_id):
    box = get_object_or_404(request.user.box_set, pk=box_id)
    if request.method == 'POST':
        box_unit = BoxUnit(box=box)
        form = CreateBoxUnitForm(request.POST, instance=box_unit)
        if form.is_valid():
            # because box isn't part of the form, we have to validate uniqueness ourselves
            try:
                box_unit.validate_unique()
                form.save()
                return JsonResponse({"success": True, "id": box_unit.id})
            except ValidationError as ex:
                return JsonResponse({"success": False, "errors": [str(ex)]})
        else:
            return JsonResponse({"success": False, "errors": form.errors.get_json_data()})
    elif request.method == 'GET':
        return JsonResponse({"units": [{"id": u.id, "name": u.name, "range": u.search_area_width, "rarity": u.rarity} for u in box.missing_units().order_by('search_area_width')]})
    else:
        raise SuspiciousOperation()

@login_required
def alter_box(request : HttpRequest, box_id):
    if request.user.single_mode:
        raise SuspiciousOperation("Trying to edit/delete box in single mode")
    box = get_object_or_404(request.user.box_set, pk=box_id)
    if request.method == 'POST':
        form = BoxForm(request.POST, instance=box)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Invalid box"})
    elif request.method == 'DELETE':
        box.delete()
        return JsonResponse({"success": True})
    else:
        raise SuspiciousOperation()

@login_required
def create_box(request : HttpRequest):
    if request.user.single_mode:
        raise SuspiciousOperation("Trying to create box in single mode")
    if request.method == 'POST':
        form = BoxForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return JsonResponse({"success": True, "id": form.instance.id})
        else:
            return JsonResponse({"success": False, "error": "Invalid box"})
    else:
        raise SuspiciousOperation()

@login_required
def index(request : HttpRequest):
    request.user.check_single_mode()
    return render(request, 'rong/box/index.html', {})
