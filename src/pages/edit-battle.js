import {hide_loading, make_alert, page, show_loading} from '../modules/common';
import $ from "jquery";

require("datatables.net-bs4/js/dataTables.bootstrap4");

page('clan_edit_battle', function () {
    $(".delete-group-button").click(function() {
        let $row = $(this).closest("tr");
        let url = $(this).attr("data-url");
        let d = $("<div>Are you sure you want to delete the hit group <span class='name'></span>? This cannot be undone.</div>");
        d.find(".name").html($row.attr("data-name"));
        d.dialog(
            {
                buttons: {
                    "Yes": function () {
                        d.dialog('destroy');
                        show_loading();
                        $.ajax({
                            url: url,
                            beforeSend: function (xhr) {
                                xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
                            },
                            type: 'DELETE',
                            success: function (data) {
                                if (data.success) {
                                    location.reload();
                                } else {
                                    make_alert($('#mainContent'), 'danger', 'Hit group could not be removed.');
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
    $(".delete-comp-button").click(function() {
        let $row = $(this).closest("tr");
        let url = $(this).attr("data-url");
        let d = $("<div>Are you sure you want to delete the comp <span class='name'></span>? This cannot be undone.</div>");
        d.find(".name").html($row.attr("data-name"));
        d.dialog(
            {
                buttons: {
                    "Yes": function () {
                        d.dialog('destroy');
                        show_loading();
                        $.ajax({
                            url: url,
                            beforeSend: function (xhr) {
                                xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
                            },
                            type: 'DELETE',
                            success: function (data) {
                                if (data.success) {
                                    location.reload();
                                } else {
                                    make_alert($('#mainContent'), 'danger', 'Comp could not be removed.');
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
