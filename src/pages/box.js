import $ from 'jquery';
import {
    show_loading, hide_loading, make_alert, icon_id, rank_color, unit_position
} from '../modules/common';
import {boxUnitModal} from "../modules/box-unit-modal";
import 'jquery-validation';

$(document).ready(function () {
    let boxes = {};

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
            alert("Please select a unit to add!");
            return false;
        }
        let unit_id = $('#addUnitForm input:checked').val();
        $('#addUnitModal').modal('hide');
        show_loading();
        $.post("/box/" + id + "/unit/create/", $('#addUnitForm').serialize(), function (data) {
            if (data.success) {
                boxes[id].units[data.unit.id] = data.unit;
                renderBoxUnits(id);
                make_alert($('#mainContent'), 'success', 'Unit added to box.');
            } else {
                make_alert($('#mainContent'), 'danger', 'Unit could not be added to box.');
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
                    unit_selector += '<input type="radio" name="unit" value="' + unit.id + '" />';
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
            let bcf = $('#boxClanField');
            bcf.empty();
            bcf.append($("<option selected></option>").attr("value", "").text("--None--"));
            for (let clan of data.clan_options) {
                bcf.append($("<option></option>").attr("value", clan[0]).text(clan[1]));
            }
            bcf.prop("disabled", data.clan_options.length == 0 ? "disabled" : false);
            if (data.clan) {
                bcf.val(data.clan);
            }
            $('#boxNameField').val(data.name);
            $('#boxSaveBtn').off('click');
            $('#boxSaveBtn').click(function () {
                doEditBox(id);
            });
            $('#boxModal').modal();
        }, "json");
    }

    function doCreateBox() {
        $('#boxForm').validate();
        if ($('#boxForm').valid()) {
            $('#boxModal').modal('hide');
            show_loading();
            $.post("/box/create/", $('#boxForm').serialize(), function (data) {
                if (data.success) {
                    boxes[data.box.id] = data.box;
                    renderBoxes();
                    make_alert($('#mainContent'), 'success', 'Box created successfully.');
                } else {
                    make_alert($('#mainContent'), 'danger', 'Could not create box.');
                }
                hide_loading();
            });
        }
    }

    function createBox() {
        show_loading();
        $.get("/box/create/", function (data) {
            hide_loading();
            $('#boxModalLabel').text('Create Box');
            let bcf = $('#boxClanField');
            bcf.empty();
            bcf.append($("<option selected></option>").attr("value", "").text("--None--"));
            for (let clan of data.clan_options) {
                bcf.append($("<option></option>").attr("value", clan[0]).text(clan[1]));
            }
            bcf.prop("disabled", data.clan_options.length == 0 ? "disabled" : false);
            $('#boxNameField').val("");
            $('#boxSaveBtn').off('click');
            $('#boxSaveBtn').click(doCreateBox);
            $('#boxModal').modal();
        }, "json");
    }

    function renderBoxes() {
        $('#boxes').empty();
        for (const id in boxes) {
            const box = boxes[id];
            // Render the box itself
            let boxEle = $("#boxTemplate").clone().removeClass("template").attr("id", "box-" + box.id);
            boxEle.find(".name").text(box.name);
            boxEle.find(".box-clan-name").text(box.clan);
            boxEle.find(".box-load-screenshot").click(function () {
                alert("Soon™");
            });
            boxEle.find(".box-edit").click(function () {
                editBox(id);
            });
            boxEle.find(".box-delete").click(function () {
                doDeleteBox(id);
            });
            boxEle.appendTo("#boxes");
            renderBoxUnits(id);
        }
    }

    function setupBoxes() {
        let rawBoxes = JSON.parse(document.getElementById('boxData').textContent);
        for (const box of rawBoxes) {
            boxes[box.id] = box;
        }
        renderBoxes();
    }

    if($(".page__box_index").length) {
        $('#addUnitModal ul.position-selector li').click(function () {
            addUnitFilter($(this).attr('data-filter'));
        });

        $('#createBoxBtn').click(createBox);

        setupBoxes();
    }
});
