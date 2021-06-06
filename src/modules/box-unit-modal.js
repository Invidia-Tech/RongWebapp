import $ from 'jquery';
import {
    icon_id, rank_color, equipment_stars
} from './common';
import {equipmentData} from "./equipment";
import 'jquery-ui/ui/widgets/dialog';

let current_unit = null;
let setting_up = false;
let equipped_all_slots = false;
let refined_all_slots = false;
let dirty = false;
let MAX_STAR = 5;
let editable = false;
let saveFn = null;
let deleteFn = null;
let deleteText = null;

function renderUnitStars() {
    for (let star = 1; star <= MAX_STAR; star++) {
        $(".unit-star-holder span.star[data-num='" + star + "']").toggleClass("active", current_unit.star >= star);
    }
}

function equipAll(refine) {
    if (!editable) {
        return;
    }
    let current_equips = current_unit.ranks[current_unit.rank - 1];
    for (let slot = 1; slot <= 6; slot++) {
        if (current_equips[slot - 1] == 999999) {
            current_unit["equip" + slot] = null;
        } else {
            let stars = equipment_stars(equipmentData[current_equips[slot - 1]].promotion_level);
            if (refine) {
                current_unit["equip" + slot] = stars;
            } else {
                current_unit["equip" + slot] = (current_unit["equip" + slot] === null) ? 0 : current_unit["equip" + slot];
            }
        }
    }
    renderEquips();
}

function renderEquips() {
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
        } else {
            // make sure both images are loaded at once
            let equip_info = equipmentData[equip];
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
            } else {
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

    $("#boxUnitEquipAllBtn").text(equipped_all_slots ? "Unequip All" : "Equip All");
    $("#boxUnitRefineAllBtn").text(refined_all_slots ? "Unrefine All" : "Refine All");
    renderPreview();
}

function renderPreview() {
    let unit_el = '<div class="unit-icon u-' + icon_id(current_unit.unit.id, current_unit.star) + '">';
    unit_el += '<i class="unit-icon-border ' + rank_color(current_unit.rank) + '"></i>';
    unit_el += '<div class="unit-icon-stars s-' + current_unit.star + '"></div>';
    unit_el += '</div>';
    $('#boxUnitForm .unit-preview-holder').html(unit_el);
}

function deleteUnit() {
    if (!editable) {
        return;
    }
    let d = $(deleteText);
    d.find(".unit-name").text(current_unit.unit.name);
    d.dialog(
        {
            buttons: {
                "Yes": function () {
                    d.dialog('destroy');
                    dirty = false;
                    $('#boxUnitModal').modal('hide');
                    deleteFn();
                },
                "No": function () {
                    d.dialog('destroy');
                },
            },
            appendTo: '#boxUnitModal',
            modal: true,
        }
    );
}

function save() {
    if (!editable) {
        return;
    }
    dirty = false;
    $('#boxUnitModal').modal('hide');
    if (saveFn) {
        saveFn({
            csrfmiddlewaretoken: $('#boxUnitForm input[name="csrfmiddlewaretoken"]').val(),
            level: current_unit.level,
            star: current_unit.star,
            rank: current_unit.rank,
            equip1: current_unit.equip1,
            equip2: current_unit.equip2,
            equip3: current_unit.equip3,
            equip4: current_unit.equip4,
            equip5: current_unit.equip5,
            equip6: current_unit.equip6,
        });
    }
}

export function boxUnitModal (data, options) {
    options = $.extend({}, boxUnitModal.defaults, options);
    editable = options.editable;
    saveFn = options.saveFunction;
    deleteFn = options.deleteFunction;
    deleteText = options.deleteText;

    setting_up = true;
    dirty = false;
    current_unit = $.extend({}, data);

    let title = $("<span>" + options.titleText + "</span>");
    title.find(".unit-name").text(current_unit.unit.name);
    $('#boxUnitModalLabel').html(title.html());

    if (!current_unit.rank) {
        current_unit.rank = 1;
    }
    if (current_unit.rank > current_unit.ranks.length) {
        current_unit.rank = current_unit.ranks.length;
    }
    if (!current_unit.level) {
        current_unit.level = 1;
    }

    renderEquips();
    let rank_field = $('#boxUnitRankField');
    rank_field.attr("min", 1);
    rank_field.attr("max", current_unit.ranks.length);
    rank_field.val(current_unit.rank);

    for (let star = 1; star <= MAX_STAR; star++) {
        $(".unit-star-holder span.star[data-num='" + star + "']").toggleClass("selectable", current_unit.unit.rarity <= star);
    }
    renderUnitStars();

    let level_field = $('#boxUnitLevelField');
    level_field.attr("min", 1);
    level_field.attr("max", current_unit.max_level);
    level_field.val(current_unit.level);

    // editable?
    if (editable) {
        $('.boxUnitAction').show();
        rank_field.attr('disabled', false);
        level_field.attr('disabled', false);
    } else {
        $('.boxUnitAction').hide();
        rank_field.attr('disabled', 'disabled');
        level_field.attr('disabled', 'disabled');
    }

    // done
    setting_up = false;
    $('#boxUnitModal').modal();
}

boxUnitModal.defaults = {
    editable: false,
    saveFunction: null,
    deleteFunction: null,
    deleteText: null,
    titleText: "Unit - <span class='unit-name'></span>"
};

$(document).ready(function () {
    $('#boxUnitRankField').change(function () {
        if (setting_up) {
            return;
        }
        let new_rank = $('#boxUnitRankField').val();
        if (new_rank <= 0 || new_rank > current_unit.ranks.length) {
            setting_up = true;
            new_rank = Math.min(Math.max(1, new_rank), current_unit.ranks.length);
            $('#boxUnitRankField').val(new_rank);
            setting_up = false;
        }
        current_unit.rank = new_rank;
        for (let slot = 1; slot <= 6; slot++) {
            current_unit["equip" + slot] = null;
        }
        dirty = true;
        renderEquips();
    });

    $('#boxUnitRankMaxBtn').click(function () {
        $('#boxUnitRankField').val(current_unit.ranks.length).change();
    });

    $('.unit-star-holder span.star').click(function () {
        if (!editable) {
            return;
        }
        let star = parseInt($(this).attr('data-num'));
        if (setting_up) {
            return;
        }
        if (star < current_unit.unit.rarity) {
            return;
        }
        current_unit.star = parseInt(star);
        dirty = true;
        renderUnitStars();
        renderPreview();
    });

    $('#boxUnitLevelField').change(function () {
        if (setting_up) {
            return;
        }
        let new_level = $('#boxUnitLevelField').val();
        if (new_level <= 0 || new_level > current_unit.max_level) {
            setting_up = true;
            new_level = Math.min(Math.max(1, new_level), current_unit.max_level);
            $('#boxUnitLevelField').val(new_level);
            setting_up = false;
        }
        current_unit.level = new_level;
        dirty = true;
    });

    $('#boxUnitLevelMaxBtn').click(function () {
        $('#boxUnitLevelField').val(current_unit.max_level).change();
    });

    $('#boxUnitMaxAllBtn').click(function () {
        $('#boxUnitRankField').val(current_unit.ranks.length).change();
        current_unit.star = MAX_STAR;
        renderUnitStars();
        $('#boxUnitLevelField').val(current_unit.max_level).change();
        equipAll(true);
    });

    $('#boxUnitMinAllBtn').click(function () {
        $('#boxUnitRankField').val(1).change();
        current_unit.star = current_unit.unit.rarity;
        renderUnitStars();
        $('#boxUnitLevelField').val(1).change();
    });

    $('#boxUnitEquipAllBtn').click(function () {
        if (equipped_all_slots) {
            // unequip all
            for (let slot = 1; slot <= 6; slot++) {
                current_unit["equip" + slot] = null;
            }
            renderEquips();
        } else {
            equipAll(false);
        }
        dirty = true;
    });

    $('#boxUnitRefineAllBtn').click(function () {
        if (refined_all_slots) {
            // unrefine all
            for (let slot = 1; slot <= 6; slot++) {
                if (current_unit["equip" + slot] !== null) {
                    current_unit["equip" + slot] = 0;
                }
            }
            renderEquips();
        } else {
            equipAll(true);
        }
        dirty = true;
    })

    $('#boxUnitModal .equip-holder img').click(function () {
        if (!editable) {
            return;
        }
        let slot = parseInt($(this).parent().attr('data-slot'));
        let equip = current_unit.ranks[current_unit.rank - 1][slot - 1];
        if (equip == 999999) {
            // no gear in this slot, do nothing
            return;
        }
        if (current_unit["equip" + slot] === null) {
            // currently unequipped, equip with no refines
            current_unit["equip" + slot] = 0;
        } else {
            // currently equipped, unequip
            current_unit["equip" + slot] = null;
        }
        renderEquips();
        dirty = true;
    });

    $('#boxUnitModal .equip-holder span.star').click(function () {
        if (!editable) {
            return;
        }
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
        } else {
            // star amount change or equip
            current_unit["equip" + slot] = star;
        }

        renderEquips();
        dirty = true;
    });

    $('#boxUnitModal').on('hide.bs.modal', function (e) {
        if (editable && dirty) {
            e.preventDefault();
            e.stopImmediatePropagation();
            let dialog = $('<p>You have unsaved changes. Save them?</p>').dialog(
                {
                    buttons: {
                        "Yes": function () {
                            dialog.dialog('destroy');
                            save();
                        },
                        "No": function () {
                            dialog.dialog('destroy');
                            dirty = false;
                            $('#boxUnitModal').modal('hide');
                        },
                        "Cancel": function () {
                            dialog.dialog('destroy');
                        }
                    },
                    appendTo: '#boxUnitModal',
                    modal: true,
                }
            );
            return false;
        }
    });

    $('#boxUnitSaveBtn').click(save);
    $('#boxUnitRemoveBtn').click(deleteUnit);
});
