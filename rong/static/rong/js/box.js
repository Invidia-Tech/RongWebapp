$(document).ready(function () {
    let boxes = {};
    let current_unit = null;
    let setting_up = false;
    let equipped_all_slots = false;
    let refined_all_slots = false;
    let dirty = false;
    let MAX_STAR = 5;

    $('#rankField').change(function () {
        if (setting_up) {
            return;
        }
        current_unit.rank = parseInt($('#rankField').val());
        for (let slot = 1; slot <= 6; slot++) {
            current_unit["equip" + slot] = null;
        }
        dirty = true;
        editUnitRenderEquips();
    });

    $('#rankMaxBtn').click(function () {
        $('#rankField').val(current_unit.ranks.length).change();
    });

    $('#starField').change(function () {
        if (setting_up) {
            return;
        }
        current_unit.star = parseInt($('#starField').val());
        dirty = true;
        editUnitRenderPreview();
    });

    $('#starMaxBtn').click(function () {
        $('#starField').val(MAX_STAR).change();
    });

    $('#levelField').change(function () {
        if (setting_up) {
            return;
        }
        current_unit.level = $('#levelField').val();
        dirty = true;
    });

    $('#levelMaxBtn').click(function () {
        $('#levelField').val(current_unit.max_level).change();
    });

    $('#editUnitMaxAllBtn').click(function () {
        $('#rankField').val(current_unit.ranks.length).change();
        $('#starField').val(MAX_STAR).change();
        $('#levelField').val(current_unit.max_level).change();
        equipAll(true);
    });

    $('#editUnitMinAllBtn').click(function () {
        $('#rankField').val(1).change();
        $('#starField').val(current_unit.unit.rarity).change();
        $('#levelField').val(1).change();
    });

    $('#editUnitEquipAllBtn').click(function () {
        if (equipped_all_slots) {
            // unequip all
            for (let slot = 1; slot <= 6; slot++) {
                current_unit["equip" + slot] = null;
            }
            editUnitRenderEquips();
        }
        else {
            equipAll(false);
        }
        dirty = true;
    });

    $('#editUnitRefineAllBtn').click(function () {
        if (refined_all_slots) {
            // unrefine all
            for (let slot = 1; slot <= 6; slot++) {
                if (current_unit["equip" + slot] !== null) {
                    current_unit["equip" + slot] = 0;
                }
            }
            editUnitRenderEquips();
        }
        else {
            equipAll(true);
        }
        dirty = true;
    })

    $('#editUnitModal .equip-holder img').click(function () {
        let slot = parseInt($(this).parent().attr('data-slot'));
        let equip = current_unit.ranks[current_unit.rank - 1][slot - 1];
        if (equip == 999999) {
            // no gear in this slot, do nothing
            return;
        }
        if (current_unit["equip" + slot] === null) {
            // currently unequipped, equip with no refines
            current_unit["equip" + slot] = 0;
        }
        else {
            // currently equipped, unequip
            current_unit["equip" + slot] = null;
        }
        editUnitRenderEquips();
        dirty = true;
    });

    $('#editUnitModal .equip-holder span.star').click(function () {
        let slot = parseInt($(this).parent().attr('data-slot'));
        let star = parseInt($(this).attr('data-num'));
        let equip = current_unit.ranks[current_unit.rank - 1][slot - 1];
        if (equip == 999999) {
            // no gear in this slot, do nothing (shouldn't even be reaching here)
            return;
        }
        if (current_unit["equip" + slot] === star) {
            // they clicked on the current star amount, change to 0
            current_unit["equip" + slot] = 0;
        }
        else {
            // star amount change or equip
            current_unit["equip" + slot] = star;
        }

        editUnitRenderEquips();
        dirty = true;
    });

    $('#editUnitModal').on('hide.bs.modal', function (e) {
        if (dirty) {
            e.preventDefault();
            e.stopImmediatePropagation();
            let dialog = $('<p>You have unsaved changes. Save them?</p>').dialog(
                {
                    buttons: {
                        "Yes": function () { dialog.dialog('destroy'); doEditUnit(); },
                        "No": function () { dialog.dialog('destroy'); dirty = false; $('#editUnitModal').modal('hide'); },
                        "Cancel": function () {
                            dialog.dialog('destroy');
                        }
                    },
                    appendTo: '#editUnitModal',
                    modal: true,
                }
            );
            return false;
        }
    });

    function equipAll(refine) {
        let current_equips = current_unit.ranks[current_unit.rank - 1];
        for (let slot = 1; slot <= 6; slot++) {
            if (current_equips[slot - 1] == 999999) {
                current_unit["equip" + slot] = null;
            }
            else {
                let stars = equipment_stars(current_unit.equipment[current_equips[slot - 1]].promotion_level);
                if (refine) {
                    current_unit["equip" + slot] = stars;
                }
                else {
                    current_unit["equip" + slot] = (current_unit["equip" + slot] === null) ? 0 : current_unit["equip" + slot];
                }
            }
        }
        editUnitRenderEquips();
    }

    function editUnitRenderEquips() {
        let current_equips = current_unit.ranks[current_unit.rank - 1];
        equipped_all_slots = true;
        refined_all_slots = true;
        for (let slot = 1; slot <= 6; slot++) {
            let equip = current_equips[slot - 1];
            if (equip == 999999) {
                // unavailable equip, clear it etc
                current_unit["equip" + slot] = null;
                $("#equip-" + slot + " img.unequipped").attr("src", "/static/rong/images/equipment/999999.png").attr("title", "Nothing here...").show();
                $("#equip-" + slot + " img.equipped").hide();
                $("#equip-" + slot + " span.star").removeClass("active").addClass("disabled");
            }
            else {
                // make sure both images are loaded at once
                let equip_info = current_unit.equipment[equip];
                $("#equip-" + slot + " img.unequipped").hide().attr("src", "/static/rong/images/equipment/invalid-" + equip + ".png").attr("title", equip_info.name);
                $("#equip-" + slot + " img.equipped").hide().attr("src", "/static/rong/images/equipment/" + equip + ".png").attr("title", equip_info.name);
                let equip_stars = equipment_stars(equip_info.promotion_level);
                for (let star = 1; star <= 5; star++) {
                    $("#equip-" + slot + " span.star[data-num='" + star + "']").toggleClass("disabled", star > equip_stars);
                }
                if (current_unit["equip" + slot] === null) {
                    $("#equip-" + slot + " img.unequipped").show();
                    $("#equip-" + slot + " span.star").removeClass("active");
                    equipped_all_slots = false;
                    refined_all_slots = false;
                }
                else {
                    $("#equip-" + slot + " img.equipped").show();
                    for (let star = 1; star <= 5; star++) {
                        $("#equip-" + slot + " span.star[data-num='" + star + "']").toggleClass("active", current_unit["equip" + slot] >= star);
                    }
                    if (current_unit["equip" + slot] != equip_stars) {
                        refined_all_slots = false;
                    }
                }
            }
        }

        $("#editUnitEquipAllBtn").text(equipped_all_slots ? "Unequip All" : "Equip All");
        $("#editUnitRefineAllBtn").text(refined_all_slots ? "Unrefine All" : "Refine All");
        editUnitRenderPreview();
    }

    function editUnitRenderPreview() {
        let unit_el = '<div class="unit-icon unit-icon-' + icon_id(current_unit.unit.id, current_unit.star) + '">';
        unit_el += '<i class="unit-icon-border ' + rank_color(current_unit.rank) + '"></i>';
        unit_el += '<div class="unit-icon-stars stars-' + current_unit.star + '"></div>';
        unit_el += '</div>';
        $('#editUnitForm .unit-preview-holder').html(unit_el);
    }

    function doDeleteUnit() {
        let dialog = $('<p>Are you sure you want to remove <b>' + $('<span />').text(current_unit.unit.name).html() + '</b> from your box?</p>').dialog(
            {
                buttons: {
                    "Yes": function () {
                        dialog.dialog('destroy');
                        dirty = false;
                        $('#editUnitModal').modal('hide');
                        show_loading();
                        $.ajax({
                            url: "/box/" + current_unit.box + "/unit/" + current_unit.id + "/",
                            beforeSend: function (xhr) {
                                xhr.setRequestHeader("X-CSRFToken", $('#editUnitForm input[name="csrfmiddlewaretoken"]').val());
                            },
                            type: 'DELETE',
                            success: function (data) {
                                if (data.success) {
                                    let idx = -1;
                                    for (let i = 0; i < boxes[current_unit.box].length; i++) {
                                        if (boxes[current_unit.box][i].id == current_unit.id) {
                                            idx = i;
                                            break;
                                        }
                                    }
                                    if (idx > -1) {
                                        boxes[current_unit.box].splice(idx, 1);
                                    }
                                    renderBoxUnits(current_unit.box);
                                    make_alert($('#mainContent'), 'success', 'Unit removed from box successfully.');
                                }
                                else {
                                    make_alert($('#mainContent'), 'danger', 'Unit could not be removed.');
                                }
                                hide_loading();
                            }
                        });
                    },
                    "No": function () { dialog.dialog('destroy'); },
                },
                appendTo: '#editUnitModal',
                modal: true,
            }
        );
    }

    function doEditUnit() {
        dirty = false;
        $('#editUnitModal').modal('hide');
        let form_data = {
            csrfmiddlewaretoken: $('#editUnitForm input[name="csrfmiddlewaretoken"]').val(),
            level: current_unit.level,
            star: current_unit.star,
            rank: current_unit.rank,
            equip1: current_unit.equip1,
            equip2: current_unit.equip2,
            equip3: current_unit.equip3,
            equip4: current_unit.equip4,
            equip5: current_unit.equip5,
            equip6: current_unit.equip6,
        };
        show_loading();
        $.post("/box/" + current_unit.box + "/unit/" + current_unit.id + "/", form_data, function (data) {
            if (data.success) {
                for (let i = 0; i < boxes[current_unit.box].length; i++) {
                    if (boxes[current_unit.box][i].id == data.unit.id) {
                        boxes[current_unit.box][i] = data.unit;
                        break;
                    }
                }
                renderBoxUnits(current_unit.box);
                make_alert($('#mainContent'), 'success', 'Unit edited successfully.');
            }
            else {
                make_alert($('#mainContent'), 'danger', 'Unit could not be edited.');
            }
            hide_loading();
        });
    }

    function editUnit(box_id, unit_id) {
        show_loading();
        $.get("/box/" + box_id + "/unit/" + unit_id + "/", function (data) {
            hide_loading();
            setting_up = true;
            dirty = false;
            current_unit = data.unit;
            $('#editUnitModalLabel').text('Edit Unit - ' + current_unit.unit.name);

            if (!current_unit.rank) {
                current_unit.rank = 1;
            }
            if (current_unit.rank > current_unit.ranks.length) {
                current_unit.rank = current_unit.ranks.length;
            }
            if (!current_unit.level) {
                current_unit.level = 1;
            }

            editUnitRenderEquips();
            populateNumericDropdown('rankField', 1, current_unit.ranks.length, current_unit.rank);
            populateNumericDropdown('starField', current_unit.unit.rarity, MAX_STAR, current_unit.star);

            let level_field = $('#levelField');
            level_field.attr("min", 1);
            level_field.attr("max", current_unit.max_level);
            level_field.val(current_unit.level);

            // done
            setting_up = false;
            $('#editUnitModal').modal();
        }, "json");
    }

    function doAddUnit(id) {
        if (!$('#addUnitForm input:checked').length) {
            alert("Please select a unit to add!");
            return false;
        }
        let unit_id = $('#addUnitForm input:checked').val();
        $('#addUnitModal').modal('hide');
        show_loading();
        $.post("/box/" + id + "/unit/create/", $('#addUnitForm').serialize(), function (data) {
            if (data.success) {
                boxes[id].push(data.unit);
                renderBoxUnits(id);
                make_alert($('#mainContent'), 'success', 'Unit added to box.');
            }
            else {
                make_alert($('#mainContent'), 'danger', 'Unit could not be added to box.');
            }
            hide_loading();
        });
    }

    function addUnitFilter(filter) {
        if (filter == 'all') {
            $('#addUnitForm label').show();
        }
        else {
            $('#addUnitForm label').hide();
            $('#addUnitForm label.position-' + filter).show();
        }
        // uncheck the checked unit if hidden
        $('#addUnitForm input:checked').each(function () {
            if ($(this).is(':hidden')) {
                this.checked = false;
            }
        });
        $('#addUnitModal ul.position-selector li').removeClass('active');
        $('#addUnitModal ul.position-selector li[data-filter="' + filter + '"]').addClass('active');
    }

    function addUnit(id) {
        show_loading();
        $.get("/box/" + id + "/unit/create/", function (data) {
            hide_loading();
            $('#addUnitModal ul.position-selector li').removeClass('active');
            $('#addUnitModal ul.position-selector li[data-filter="all"]').addClass('active');
            if (data.units.length == 0) {
                $('#addUnitModal .add-button').prop('disabled', true);
                $('#addUnitForm .units').html('<p>You already have every unit in your box!</p>');
            }
            else {
                $('#addUnitModal .add-button').prop('disabled', false);
                let addunit_form = $('#addUnitForm .units');
                addunit_form.html('');
                for (unit of data.units) {
                    let unit_selector = '<label class="image-radio position-' + unit_position(unit.range) + '" title="' + unit.name + '">';
                    unit_selector += '<input type="radio" name="unit" value="' + unit.id + '" />';
                    unit_selector += '<div class="unit-icon unit-icon-' + icon_id(unit.id, unit.rarity) + '">';
                    unit_selector += '<i class="unit-icon-border white"></i>';
                    unit_selector += '<div class="unit-icon-stars stars-' + unit.rarity + '"></div>';
                    unit_selector += '</div>';
                    unit_selector += '</label>';
                    addunit_form.append(unit_selector);
                }
            }
            $('#addUnitModal .add-button').off('click');
            $('#addUnitModal .add-button').click(function () {
                doAddUnit(id);
            });
            $('#addUnitModal').modal();
        }, "json");
    }

    function renderBoxUnits(id) {
        let box_selector = '#box-' + id;
        let box_data = boxes[id];
        let box_units_el = $(box_selector + ' .box-units');
        box_units_el.html('');
        for (const unit of box_data) {
            let unit_el = '<div class="unit-icon unit-icon-' + icon_id(unit.unit_id, unit.star) + '" data-id="' + unit.id + '">';
            unit_el += '<i class="unit-icon-border ' + rank_color(unit.rank) + '"></i>';
            if (unit.star) {
                unit_el += '<div class="unit-icon-stars stars-' + unit.star + '"></div>';
            }
            unit_el += '</div>';
            box_units_el.append(unit_el);
        }
        box_units_el.append("<div class='box-units-add'></div>");
        $(box_selector + ' .unit-icon').click(function () {
            editUnit(id, $(this).attr("data-id"));
        });
        $(box_selector + ' .box-units-add').click(function () {
            addUnit(id);
        });
    }

    $('.box').each(function () {
        let id = $(this).attr("data-id");
        boxes[id] = JSON.parse($(this).attr("data-units"));
        renderBoxUnits(id);
    });

    $('#addUnitModal ul.position-selector li').click(function () {
        addUnitFilter($(this).attr('data-filter'));
    });

    $('.box-load-screenshot').click(function () {
        alert("Soon™");
    });

    $('#editUnitSaveBtn').click(doEditUnit);
    $('#editUnitRemoveBtn').click(doDeleteUnit);
});
