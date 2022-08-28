import $ from 'jquery';
import {getDescendantProp, hide_loading, make_alert, page, show_loading} from '../modules/common';
import 'jquery-validation';
import 'datatables.net';
import 'datatables.net-rowreorder';
let page_function = function () {
    let $hitLog = $('#hitLogTable');
    let manageable = $hitLog.hasClass('manageable');
    let bulkPilotMode = false;
    let fullData = null;
    let columns = [
        {orderable: false, data: null, defaultContent: "<span class=\"grippy\"></span>"},
        {data: "order"},
        {data: "day"},
        {data: "username"},
        {
            data: "pilot",
            render: function (data, type, row) {
                if(type == 'sort') {
                    return data;
                }
                if(bulkPilotMode) {
                    let selector = $("<select class='bulk-pilot'></select>");
                    selector.attr("data-id", row.id);
                    selector.attr("data-original", row.pilot_id);
                    for(let choice of fullData.pilot_choices) {
                        let option = $("<option></option>");
                        option.attr("value", choice[0]);
                        option.text(choice[1]);
                        if(choice[0] == row.pilot_id) {
                            option.attr("selected", true);
                        }
                        selector.append(option);
                    }
                    return selector.outerHTML();
                }
                else {
                    return data;
                }
            }
        },
        {
            data: "team",
            orderable: false,
            render: function (data) {
                if (data === false) {
                    return 'N/A';
                }
                let units = '';
                for (let unit of data) {
                    let icon = $("<div class='unit-ddicon'></div>");
                    icon.addClass('u-' + unit.icon);
                    icon.attr('title', unit.name);
                    units += icon.outerHTML();
                }
                return units;
            },
        },
        {
            data: "damage",
            render: function (data, type) {
                if(window.location.href.includes("hitsactual")) {
                    return data.actual;
                }
                if (type == 'sort') {
                    return data.damage;
                }
                if (data.damage === data.actual) {
                    return data.damage.toLocaleString();
                } else {
                    let dmg = $("<span class='underline-dotted'></span>");
                    dmg.text(data.damage.toLocaleString());
                    dmg.attr('title', data.actual.toLocaleString() + ' actual damage');
                    return dmg.outerHTML();
                }
            },
        },
        {data: "lap", orderable: false},
        {
            data: "boss",
            render: function (data, type) {
                if (type == 'sort') {
                    return data.number;
                }
                let img = $("<img style='width: 32px; height: 32px;' />");
                img.attr("src", '/static/rong/images/enemies/' + data.icon + '.png');
                img.attr("alt", data.name);
                img.attr("title", data.name);
                return img.outerHTML();
            }
        },
        {data: "hp_left", orderable: false, render: (data) => data.toLocaleString()},
        {
            data: "attempts",
            orderable: false,
            render: function (data) {
                return data.value + '/' + data.per_day;
            },
        },
        {data: "hit_type"},
        {
            data: "links",
            orderable: false,
            render: function (data) {
                let editBtn = $('<a class="btn btn-primary" title="Edit"><i class="fa fa-edit"></i></a>');
                editBtn.attr("href", data.edit_url);
                return editBtn.outerHTML() + ' <button class="btn btn-danger delete-button" title="Delete"><i class="fa fa-remove"></i></button>';
            }
        },
    ];
    if (!manageable) {
        // first and last columns are lead-only (reorder and actions)
        columns.pop();
        columns.shift();
    }
    let opts = {
        ajax: {
            url: $("#hitLogData").attr("data-url"),
            dataSrc: "hits",
        },
        columns: columns,
        order: [[manageable ? 1 : 0, "desc"]],
        autoWidth: false,
        lengthMenu: [[100,200,-1], [100,200,"All"]]
    };
    if (manageable) {
        opts.rowReorder = {
            selector: 'span.grippy',
            dataSrc: "order",
        };
    }
    let table = $hitLog.DataTable(opts);
    table.on('draw.dt', function () {
        let $deleteButtons = $("#hitLogTable .delete-button");
        $deleteButtons.off("click");
        $deleteButtons.click(function () {
            let data = table.row($(this).closest("tr")).data();
            console.log(data);
            let d = $("<div>Are you sure you want to delete <span class='name'></span>'s hit for <span class='damage'></span> damage? This cannot be undone.</div>");
            d.find(".name").html(data.username);
            d.find(".damage").text(data.damage.damage.toLocaleString());
            d.dialog(
                {
                    buttons: {
                        "Yes": function () {
                            d.dialog('destroy');
                            show_loading();
                            $.ajax({
                                url: data.links.edit_url,
                                beforeSend: function (xhr) {
                                    xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
                                },
                                type: 'DELETE',
                                success: function (data) {
                                    if (data.success) {
                                        location.reload();
                                    } else {
                                        make_alert($('#mainContent'), 'danger', 'Hit could not be removed.');
                                    }
                                    hide_loading();
                                }
                            });
                        },
                        "No": function () {
                            d.dialog('destroy');
                        },
                    },
                    modal: true,
                }
            );

        });
    });
    table.on('row-reorder', function (e, diff, edit) {
        if (diff.length > 0) {
            let reorderData = {};
            diff.forEach(function (change) {
                reorderData[table.row(change.node).data().id] = change.newData;
            });
            show_loading();
            $('#reorderData').val(JSON.stringify(reorderData));
            $('#reorderForm').submit();
        }
    });
    table.on('xhr.dt', function (e, settings, json, xhr) {
        // populate filters for tags and groups from json
        fullData = json;
        if (manageable) {
            let filters = [
                {
                    name: "Account",
                    control: "dropdown_isnot",
                    choices: json.members,
                    column: 'member_id'
                },
                {
                    name: "Damage",
                    control: "number",
                    column: "damage.damage"
                },
                {
                    name: "Hit #",
                    control: "number",
                    column: "order"
                },
                {
                    name: "Day",
                    control: "number",
                    column: "day"
                },
                {
                    name: "Lap",
                    control: "number",
                    column: "lap"
                },
                {
                    name: "Boss",
                    control: "dropdown_isnot",
                    choices: json.boss_choices,
                    column: 'boss.number'
                },
                {
                    name: "Unit",
                    control: "custom",
                    comparisons: ["in team", "not in team"],
                    inputType: "dropdown",
                    choices: json.unit_choices,
                    callback: function (data, comparison, value) {
                        value = parseInt(value);
                        if (data.team === false) {
                            return false;
                        }
                        for (let unit of data.team) {
                            if (value == unit.unit) {
                                return comparison == 'in team';
                            }
                        }
                        return comparison != 'in team';
                    }
                },
                {
                    name: "Hit Type",
                    control: "dropdown_isnot",
                    choices: [["Normal", "Normal"], ["Last Hit", "Last Hit"], ["Carryover", "Carryover"]],
                    column: 'hit_type'
                },
                {
                    name: "Hit Group",
                    control: "dropdown_isnot",
                    choices: json.groups,
                    column: 'group'
                },
                {
                    name: "Tag",
                    control: "custom",
                    comparisons: ["is tagged", "not tagged"],
                    inputType: "dropdown",
                    choices: json.tags,
                    callback: function (data, comparison, value) {
                        value = parseInt(value);
                        let tag_present = data.tags.indexOf(value) > -1;
                        return tag_present == (comparison == 'is tagged');
                    }
                },
                {
                    name: "Phase",
                    control: "number",
                    column: "phase"
                },
                {
                    name: "Comp",
                    control: "dropdown_isnot",
                    choices: json.comps,
                    column: 'comp'
                },
                {
                    name: "Boss Code",
                    control: "dropdown_isnot",
                    choices: json.boss_codes,
                    column: 'boss_code'
                },
                {
                    name: "Player",
                    control: "dropdown_isnot",
                    choices: json.players,
                    column: 'player_id'
                },
                {
                    name: "Pilot",
                    control: "dropdown_isnot",
                    choices: json.pilots,
                    column: 'pilot_id'
                },
            ];
            let filtersByName = {};
            for (let filter of filters) {
                filtersByName[filter.name] = filter;
                if (filter.control == 'dropdown_isnot') {
                    filter.comparisons = ["is", "is not"];
                    filter.inputType = "dropdown";
                    filter.callback = function (data, comparison, value) {
                        let dataValue = getDescendantProp(data, filter.column);
                        let valueEqual = value == dataValue;
                        return valueEqual == (comparison == 'is');
                    }
                } else if (filter.control == 'number') {
                    filter.comparisons = ["==", "!=", ">=", ">", "<=", "<"];
                    filter.inputType = "number";
                    filter.callback = function (data, comp, value) {
                        let compVal = getDescendantProp(data, filter.column);
                        let numVal = parseInt(value);
                        return (comp == '==' && compVal == numVal) || (comp == '!=' && compVal != numVal) || (comp == '>=' && compVal >= numVal) || (comp == '>' && compVal > numVal) || (comp == '<=' && compVal <= numVal) || (comp == '<' && compVal < numVal);
                    }
                }
            }
            let currentFilters = [];
            let $filterBox = $("#filters");
            $filterBox.show();
            $("#addFilter").click(function () {
                let $filter = $("<div class='filter'></div>");
                let currentFilter = {type: '', comparison: '', value: ''};
                currentFilters.push(currentFilter);

                let $selector = null;
                let $comparisonSelector = null;
                let $valueInput = null;
                let $deleteBtn = $("<button class='btn btn-danger'><i class='fa fa-remove'></i></button>");

                function selectorChange() {
                    currentFilter.type = $selector.val();
                    currentFilter.comparison = '';
                    currentFilter.value = '';
                    if ($comparisonSelector) {
                        $comparisonSelector.remove();
                    }
                    if ($valueInput) {
                        $valueInput.remove();
                    }
                    let filter = filtersByName[currentFilter.type];
                    $comparisonSelector = $("<select></select>");
                    for (let comparison of filter.comparisons) {
                        let $option = $("<option></option>");
                        $option.attr("value", comparison);
                        $option.text(comparison);
                        $comparisonSelector.append($option);
                    }
                    currentFilter.comparison = filter.comparisons[0];
                    $comparisonSelector.insertBefore($deleteBtn);
                    if (filter.inputType == 'number') {
                        $valueInput = $('<input type="number" />');
                    } else {
                        $valueInput = $("<select><option value=''>Select...</option></select>");
                        for (let choice of filter.choices) {
                            let $option = $("<option></option>");
                            $option.attr("value", choice[0]);
                            $option.text(choice[1]);
                            $valueInput.append($option);
                        }
                    }
                    $valueInput.insertBefore($deleteBtn);
                    attachEvents();
                    table.draw();
                }

                function compSelectorChange() {
                    currentFilter.comparison = $comparisonSelector.val();
                    table.draw();
                }

                function valueInputChange() {
                    currentFilter.value = $valueInput.val();
                    table.draw();
                }

                function attachEvents() {
                    if ($selector) {
                        $selector.off("change").change(selectorChange);
                    }
                    if ($comparisonSelector) {
                        $comparisonSelector.off("change").change(compSelectorChange);
                    }
                    if ($valueInput) {
                        $valueInput.off("change").change(valueInputChange);
                    }
                }

                $selector = $("<select><option value=''>Select...</option></select>");
                for (let filter of filters) {
                    let $option = $("<option></option>");
                    $option.attr("value", filter.name);
                    $option.text(filter.name);
                    $selector.append($option);
                }
                $filter.append($selector);
                $filter.append($deleteBtn);
                $deleteBtn.click(function () {
                    $filter.remove();
                    const index = currentFilters.indexOf(currentFilter);
                    if (index > -1) {
                        currentFilters.splice(index, 1);
                    }
                    table.draw();
                })
                attachEvents();

                // do last
                $filter.appendTo($filterBox);
            });

            $.fn.dataTable.ext.search.push(
                function (settings, data, dataIndex) {
                    data = json.hits[dataIndex];
                    for (let currentFilter of currentFilters) {
                        if (currentFilter.type == '' || currentFilter.comparison == '' || currentFilter.value == '') {
                            continue;
                        }
                        let filter = filtersByName[currentFilter.type];
                        if (!filter.callback(data, currentFilter.comparison, currentFilter.value)) {
                            return false;
                        }
                    }
                    return true;
                }
            );

            $("#bulkPilotBtn").prop("disabled", false).click(function() {
                if(bulkPilotMode) {
                    // submit
                    let updateMap = {};
                    let numUpdates = 0;
                    $(".bulk-pilot").each(function() {
                        let $t = $(this);
                        if($t.attr("data-original") != $t.val()) {
                            updateMap[$t.attr("data-id")] = $t.val();
                            numUpdates++;
                        }
                    });
                    if(numUpdates == 0) {
                        alert("You didn't update any pilots!");
                        return;
                    }
                    show_loading();
                    $('#pilotData').val(JSON.stringify(updateMap));
                    $('#bulkPilotForm').submit();
                }
                else {
                    bulkPilotMode = true;
                    table.rows().invalidate().draw( false );
                    $("#bulkPilotBtn").text("Save Pilots");
                }
            });
        }
    });


}

page('cb_list_hits', page_function);
page('cb_list_hitsa', page_function);

