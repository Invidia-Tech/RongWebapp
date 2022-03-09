import $ from 'jquery';
import {hide_loading, icon_id, make_alert, rank_color, show_loading, unit_position} from './common';
import {boxUnitModal} from "./box-unit-modal";
import 'jquery-validation';

export let boxes = {};

let inventory_dirty = false;

function editUnit(box_id, unit_id) {
    boxUnitModal(boxes[box_id].units[unit_id], {
        editable: true,
        titleText: "Edit Unit - <span class='unit-name'></span>",
        saveFunction: function (form_data) {
            show_loading();
            $.post("/box/" + box_id + "/unit/" + unit_id + "/", form_data, function (data) {
                if (data.success) {
                    boxes[box_id].units[unit_id] = data.unit;
                    renderBoxUnits(box_id);
                    make_alert($('#mainContent'), 'success', 'Unit edited successfully.');
                } else {
                    make_alert($('#mainContent'), 'danger', 'Unit could not be edited.');
                }
                hide_loading();
            });
        },
        deleteText: '<p>Are you sure you want to remove <b class="unit-name"></b> from your box?</p>',
        deleteFunction: function () {
            show_loading();
            $.ajax({
                url: "/box/" + box_id + "/unit/" + unit_id + "/",
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", $('#boxUnitForm input[name="csrfmiddlewaretoken"]').val());
                },
                type: 'DELETE',
                success: function (data) {
                    if (data.success) {
                        delete boxes[box_id].units[unit_id];
                        renderBoxUnits(box_id);
                        make_alert($('#mainContent'), 'success', 'Unit removed from box successfully.');
                    } else {
                        make_alert($('#mainContent'), 'danger', 'Unit could not be removed.');
                    }
                    hide_loading();
                }
            });
        }
    });
}

function doAddUnit(id) {
    if (!$('#addUnitForm input:checked').length) {
        alert("Please select at least one unit to add!");
        return false;
    }
    $('#addUnitModal').modal('hide');
    show_loading();
    $.post("/box/" + id + "/unit/create/", $('#addUnitForm').serialize(), function (data) {
        if (data.success) {
            for (let unit of data.units) {
                boxes[id].units[unit.id] = unit;
            }
            let utext = 'Unit' + (data.units.length > 1 ? 's' : '');
            renderBoxUnits(id);
            make_alert($('#mainContent'), 'success', utext + ' added to box.');
        } else {
            make_alert($('#mainContent'), 'danger', 'Unit(s) could not be added to box.');
        }
        hide_loading();
    });
}

function addUnitFilter(filter) {
    if (filter == 'all') {
        $('#addUnitForm label').show();
    } else {
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
        } else {
            $('#addUnitModal .add-button').prop('disabled', false);
            let addunit_form = $('#addUnitForm .units');
            addunit_form.html('');
            for (let unit of data.units) {
                let unit_selector = '<label class="image-radio position-' + unit_position(unit.range) + '" title="' + unit.name + '">';
                unit_selector += '<input type="checkbox" name="units" value="' + unit.id + '" />';
                unit_selector += '<div class="unit-icon u-' + icon_id(unit.id, unit.rarity) + '">';
                unit_selector += '<i class="unit-icon-border white"></i>';
                unit_selector += '<div class="unit-icon-stars s-' + unit.rarity + '"></div>';
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
    let box_data = boxes[id].units;
    let box_units_el = $(box_selector + ' .box-units');
    box_units_el.empty();
    for (const uid in box_data) {
        const unit = box_data[uid];
        let unit_el = $("<div class='unit-icon'></div>").addClass('u-' + icon_id(unit.unit.id, unit.star));
        unit_el.append($("<i class='unit-icon-border'></i>").addClass(rank_color(unit.rank)));
        if (unit.star) {
            unit_el.append($('<div class="unit-icon-stars"></div>').addClass('s-' + unit.star));
        }
        unit_el.click(function () {
            editUnit(id, unit.id);
        });
        box_units_el.append(unit_el);
    }
    let box_unit_add = $("<div class='box-units-add'></div>");
    box_unit_add.click(function () {
        addUnit(id);
    });
    box_units_el.append(box_unit_add);
}

function doDeleteBox(id) {
    const box = boxes[id];
    let dialogText = $('<div><p>Are you sure you want to delete box <b></b> entirely?</p><p>ALL DATA WILL BE LOST.</p></div>');
    dialogText.find('b').text(box.name);
    let dialog = dialogText.dialog(
        {
            buttons: {
                "Yes": function () {
                    dialog.dialog('destroy');
                    show_loading();
                    $.ajax({
                        url: "/box/" + id + "/",
                        beforeSend: function (xhr) {
                            xhr.setRequestHeader("X-CSRFToken", $('#boxUnitForm input[name="csrfmiddlewaretoken"]').val());
                        },
                        type: 'DELETE',
                        success: function (data) {
                            if (data.success) {
                                delete boxes[id];
                                renderBoxes();
                                make_alert($('#mainContent'), 'success', 'Box deleted successfully.');
                            } else {
                                make_alert($('#mainContent'), 'danger', 'Box could not be removed.');
                            }
                            hide_loading();
                        }
                    });
                },
                "No": function () {
                    dialog.dialog('destroy');
                },
            },
            modal: true,
        }
    );
}

function doEditBox(id) {
    $('#boxForm').validate();
    if ($('#boxForm').valid()) {
        $('#boxModal').modal('hide');
        show_loading();
        $.post("/box/" + id + "/", $('#boxForm').serialize(), function (data) {
            if (data.success) {
                boxes[data.box.id] = data.box;
                renderBoxes();
                make_alert($('#mainContent'), 'success', 'Box edited successfully.');
            } else {
                make_alert($('#mainContent'), 'danger', 'Could not edit box.');
            }
            hide_loading();
        });
    }
}

function editBox(id) {
    show_loading();
    $.get("/box/" + id + "/", function (data) {
        hide_loading();
        $('#boxModalLabel').text('Edit Box');
        $('#boxNameField').val(data.name);
        $('#boxSaveBtn').off('click');
        $('#boxSaveBtn').click(function () {
            doEditBox(id);
        });
        $('#boxModal').modal();
    }, "json");
}

function saveInventory(id) {
    $('#inventoryForm').validate();
    if ($('#inventoryForm').valid()) {
        inventory_dirty = false;
        $('#inventoryModal').modal('hide');
        show_loading();
        $.post("/box/" + id + "/inventory/", $('#inventoryForm').serialize(), function (data) {
            if (data.success) {
                // Update shard count on box units
                let box_data = boxes[id].units;
                for(const item of data.inventory) {
                    if(item.id >= 31000 && item.id < 32000) {
                        let unit_id = (item.id - 30000) * 100 + 1;
                        for (const uid in box_data) {
                            if(box_data[uid].unit.id === unit_id) {
                                box_data[uid].shards = item.quantity;
                                break;
                            }
                        }
                    }
                }
                make_alert($('#mainContent'), 'success', 'Inventory edited successfully.');
            } else {
                make_alert($('#mainContent'), 'danger', 'Could not edit inventory.');
            }
            hide_loading();
        });
    }
}

function editInventory(id) {
    show_loading();
    $.get("/box/" + id + "/inventory/", function (data) {
        hide_loading();
        let inventoryHolder = $('#inventoryHolder');
        inventoryHolder.empty();
        for (const item of data) {
            let itemImage = $("<img>");
            itemImage.attr("src", '/static/rong/images/items/' + item.id + '.png');
            itemImage.attr("alt", item.name);
            itemImage.attr("title", item.name);
            let itemEle = $("<div class='col-md-2 inventory-editor-item'></div>");
            itemEle.append(itemImage);
            itemEle.append("<br />");
            let itemQty = $("<input type='number' class='form-control inventory-qty' />");
            itemQty.attr("min", 0);
            itemQty.attr("max", item.limit);
            itemQty.attr("value", item.quantity);
            itemQty.attr("name", "qty_" + item.id);
            itemEle.append(itemQty);
            inventoryHolder.append(itemEle);
        }
        $('#inventorySaveBtn').off('click').click(function () {
            saveInventory(id);
        });
        inventory_dirty = false;
        $(".inventory-qty").off('keyup').keyup(function() {
            inventory_dirty = true;
        });
        $('#inventoryModal').modal();
    }, "json");
}

export function renderBox(destination, id) {
    const box = boxes[id];
    // Render the box itself
    let boxEle = $("#boxTemplate").clone().removeClass("template").attr("id", "box-" + box.id);
    boxEle.find(".name").text(box.name);
    let actionsEle = boxEle.find(".actions");
    let armoryEle = $('<button type="button" class="btn btn-primary box-import">Import from TW Armory</button>');
    armoryEle.click(function () {
        show_loading();
        $.get("/box/" + id + "/import/", function (data) {
            hide_loading();
            $('#importModal').find('.modal-body').html(data);
            $('#importModalLabel').text('Import from TW Armory');
            $('#redirect_url').val(window.location.pathname);
            $('#importModal').modal();
        }, "html");
    });
    actionsEle.append(armoryEle);
    let loadIndexEle = $('<button type="button" class="btn btn-primary box-import">Import from /load/index</button>');
    loadIndexEle.click(function () {
        show_loading();
        $.get("/box/" + id + "/importli/", function (data) {
            hide_loading();
            $('#importModal').find('.modal-body').html(data);
            $('#importModalLabel').text('Import from /load/index');
            $('#redirect_url').val(window.location.pathname);
            $('#importModal').modal();
        }, "html");
    });
    actionsEle.append(loadIndexEle);
    let inventoryEle = $('<button type="button" class="btn btn-primary box-inventory">Edit Inventory</button>');
    inventoryEle.click(function () {
        editInventory(id);
    });
    actionsEle.append(' ');
    actionsEle.append(inventoryEle);
    if (!box.is_clan) {
        let editEle = $('<button type="button" class="btn btn-primary box-edit">Edit</button>');
        editEle.click(function () {
            editBox(id);
        });
        actionsEle.append(' ');
        actionsEle.append(editEle);
        let deleteEle = $('<button type="button" class="btn btn-danger box-delete">Delete</button>');
        deleteEle.click(function () {
            doDeleteBox(id);
        });
        actionsEle.append(' ');
        actionsEle.append(deleteEle);
    }
    boxEle.appendTo(destination);
    renderBoxUnits(id);
}

export function renderBoxes() {
    $('#boxes').empty();
    for (const id in boxes) {
        renderBox('#boxes', id);
    }
}

export function setupBoxes(rawBoxes) {
    for (const box of rawBoxes) {
        boxes[box.id] = box;
    }
}

$('#addUnitModal ul.position-selector li').click(function () {
    addUnitFilter($(this).attr('data-filter'));
});

$('#inventoryModal').on('hide.bs.modal', function (e) {
    if (inventory_dirty) {
        e.preventDefault();
        e.stopImmediatePropagation();
        let dialog = $('<p>You have unsaved changes. Save them?</p>').dialog(
            {
                buttons: {
                    "Yes": function () {
                        dialog.dialog('destroy');
                        $("#inventorySaveBtn").click();
                    },
                    "No": function () {
                        dialog.dialog('destroy');
                        inventory_dirty = false;
                        $('#inventoryModal').modal('hide');
                    },
                    "Cancel": function () {
                        dialog.dialog('destroy');
                    }
                },
                appendTo: '#inventoryModal',
                modal: true,
            }
        );
        return false;
    }
});
