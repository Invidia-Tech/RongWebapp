$(document).ready(function () {
    let boxes = {};

    function editUnit(box_id, unit_id) {
        // @TODO
        alert('Editing units soon (debug: ' + box_id + ' ' + unit_id + ')');
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
                $('#mainContent').prepend(make_alert('success', 'Unit added to box.'));
            }
            else {
                $('#mainContent').prepend(make_alert('error', 'Unit could not be added to box.'));
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
});
