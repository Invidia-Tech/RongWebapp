import $ from 'jquery';
import {
    formatDiscordName,
    formatPlayerId,
    hide_loading,
    icon_id,
    make_alert,
    page,
    rank_color,
    show_loading
} from '../modules/common';
import 'jquery-validation';
import 'jquery-mask-plugin';
import {boxUnitModal} from "../modules/box-unit-modal";

require("datatables.net-bs4/js/dataTables.bootstrap4");

page('clan_list_members', function () {
    let $api = $('.api');
    let boxes = JSON.parse(document.getElementById('boxData').textContent);

    function saveMemberDetails(id) {
        $('#editMemberForm').validate();
        if ($('#editMemberForm').valid()) {
            $('#editMemberModal').modal('hide');
            $("#id_player_id").unmask();
            show_loading();
            $.post($api.attr('data-api-url') + id + "/", $('#editMemberForm').serialize(), function (data) {
                if (data.success) {
                    let $rootRow = $("tr[data-id='" + data.member.id + "'");
                    $rootRow.find(".member-name").html(formatDiscordName(data.member.name, data.member.discriminator));
                    $rootRow.find(".member-ign").text(data.member.ign || "N/A");
                    $rootRow.find(".member-pid").text(formatPlayerId(data.member.player_id));
                    $rootRow.find(".member-group").text(data.member.group_num || "None");
                    if (data.member.is_owner) {
                        $rootRow.find(".member-lead").text("Owner");
                    } else if (data.member.is_admin) {
                        $rootRow.find(".member-lead").text("Admin");
                    } else {
                        $rootRow.find(".member-lead").text(data.member.is_lead ? "Yes" : "No");
                    }
                    make_alert($('#mainContent'), 'success', 'Member details edited successfully.');
                } else {
                    make_alert($('#mainContent'), 'danger', 'Could not edit member details.');
                }
                hide_loading();
            });
        }
    }

    function editMemberDetails(id) {
        show_loading();
        $.get($api.attr('data-api-url') + id + "/", function (member) {
            hide_loading();
            $("#editMemberName .name").text(member.name);
            $("#editMemberName .discriminator").text("#" + member.discriminator.toString().padStart(4, "0"));
            $("#id_ign").val(member.ign ?? "");
            $("#id_player_id").val(member.player_id ?? "");
            $("#id_player_id").mask('000 000 000');
            $("#id_group_num").val(member.group_num ?? "");
            if ($("#id_is_lead").length) {
                if (member.is_owner || member.is_admin) {
                    $("#id_is_lead").prop("checked", true);
                    $("#id_is_lead").prop("disabled", true);
                } else {
                    $("#id_is_lead").prop("checked", member.is_lead);
                    $("#id_is_lead").prop("disabled", false);
                }
            }
            $('#editMemberModal').modal();
            $('#editMemberSaveBtn').off('click');
            $('#editMemberSaveBtn').click(function () {
                saveMemberDetails(id);
            });
        }, 'json');
    }

    $('button.edit-member').click(function () {
        editMemberDetails($(this).closest('tr').attr('data-id'));
    });

    $('button.show-member-box').click(function () {
        let t = $('#memberListTable').DataTable();
        let btn = $(this);
        let tr = btn.closest('tr');
        let row = t.row(tr);
        let id = tr.attr("data-id");
        if (row.child.isShown()) {
            $('div.slidable', row.child()).slideUp(function () {
                row.child.hide();
                btn.text("Show");
            });
        } else {
            if (boxes[id]) {
                let box_units_el = $("<div></div>");
                let box_data = boxes[id].units;
                for (const uid in box_data) {
                    const unit = box_data[uid];
                    let unit_el = $("<div class='unit-icon clickable'></div>").addClass('u-' + icon_id(unit.unit.id, unit.star));
                    unit_el.attr("data-mid", id);
                    unit_el.attr("data-uid", uid);
                    unit_el.append($("<i class='unit-icon-border'></i>").addClass(rank_color(unit.rank)));
                    if (unit.star) {
                        unit_el.append($('<div class="unit-icon-stars"></div>').addClass('s-' + unit.star));
                    }
                    box_units_el.append(unit_el);
                }
                row.child("<div class='slidable'>" + box_units_el.html() + "</div>").show();
                $('div.slidable', row.child()).slideDown();
                btn.text("Hide");
                $("#memberListTable .unit-icon.clickable").off("click");
                $("#memberListTable .unit-icon.clickable").click(function () {
                    const unit = boxes[$(this).attr("data-mid")].units[$(this).attr("data-uid")];
                    boxUnitModal(unit, {
                        editable: false,
                        titleText: "View Unit - <span class='unit-name'></span>",
                    });
                })
            }
        }
    });
});
