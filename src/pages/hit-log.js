import $ from 'jquery';
import {hide_loading, make_alert, page, show_loading} from '../modules/common';
import 'jquery-validation';
import 'datatables.net';
import 'datatables.net-rowreorder';

page('cb_list_hits', function () {
    $("#hitLogTable .delete-button").click(function () {
        let $row = $(this).closest("tr");
        let d = $("<span>Are you sure you want to delete <span class='name'></span>'s hit for <span class='damage'></span> damage? This cannot be undone.</span>");
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
    let table = $('#hitLogTable').DataTable({
        columnDefs: [
            {orderable: false, targets: [0, 4, 6, 8, 9, 11]}
        ],
        order: [[1, "desc"]],
        rowReorder: {
            selector: 'span.grippy',
            dataSrc: 1,
        }
    });
    table.on('row-reorder', function (e, diff, edit) {
        if (diff.length > 0) {
            let reorderData = {};
            diff.forEach(function (change) {
                reorderData[$(change.node).attr("data-id")] = change.newData;
            });
            show_loading();
            $('#reorderData').val(JSON.stringify(reorderData));
            $('#reorderForm').submit();
        }
    });


});

