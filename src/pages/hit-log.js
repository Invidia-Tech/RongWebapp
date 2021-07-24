import $ from 'jquery';
import {hide_loading, make_alert, page, show_loading} from '../modules/common';
import 'jquery-validation';
import 'datatables.net';
import 'datatables.net-rowreorder';

page('cb_list_hits', function () {
    $("#hitLogTable .delete-button").click(function () {
        let $row = $(this).closest("tr");
        let d = $("<div>Are you sure you want to delete <span class='name'></span>'s hit for <span class='damage'></span> damage? This cannot be undone.</div>");
        d.find(".name").html($row.attr("data-name"));
        d.find(".damage").text($row.attr("data-damage"));
        d.dialog(
            {
                buttons: {
                    "Yes": function () {
                        d.dialog('destroy');
                        show_loading();
                        $.ajax({
                            url: "/clanbattle/" + $("#hitLogTable").attr("data-battle") + "/hits/" + $row.attr("data-id") + "/",
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
    let $hitLog = $('#hitLogTable');
    let manageable = $hitLog.hasClass('manageable');
    let columns = [
        {orderable: false, data: null, defaultContent: "<span class=\"grippy\"></span>"},
        {data: "order"},
        {data: "day"},
        {data: "username"},
        {
            data: "team",
            orderable: false,
            render: function (data) {
                if (data === false) {
                    return 'N/A';
                }
                let units = '';
                for (let unit of data) {
                    let icon = $("<div class='unit-ddicon'></div>")
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
                if(type == 'sort') {
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
                if(type == 'sort') {
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


});

