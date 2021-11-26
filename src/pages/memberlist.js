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
import {renderBox, setupBoxes} from "../modules/box-editing";

require("datatables.net-bs4/js/dataTables.bootstrap4");

page('clan_list_members', function () {
    let $api = $('.api');
    let boxes = JSON.parse(document.getElementById('boxData').textContent);

    function saveMemberDetails(id) {
        $('#memberForm').validate();
        if ($('#memberForm').valid()) {
            $('#memberModal').modal('hide');
            $("#id_player_id").unmask();
            show_loading();
            $.post($api.attr('data-api-url') + id + "/", $('#memberForm').serialize(), function (data) {
                if (data.success) {
                    let $rootRow = $("tr[data-id='" + data.member.id + "'");
                    if(data.member.discord_id) {
                        $rootRow.find(".member-discord").html(formatDiscordName(data.member.discord_username, data.member.discord_discriminator));
                    }
                    else {
                        $rootRow.find(".member-discord").html('N/A');
                    }
                    $rootRow.find(".member-ign").text(data.member.ign);
                    $rootRow.find(".member-pid").text(formatPlayerId(data.member.player_id));
                    if (data.member.is_admin) {
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

    function memberDetails(id) {
        show_loading();
        $.get($api.attr('data-api-url') + id + "/", function (member) {
            hide_loading();
            $("#id_ign").val(member.ign ?? "");
            $("#id_player_id").val(member.player_id ? formatPlayerId(member.player_id) : "");
            $("#id_player_id").mask('000 000 000');
            $("#id_group_num").val(member.group_num ?? "");
            $("#id_discord").val(member.discord_id ?? "");
            if ($("#id_is_lead").length) {
                if (member.is_admin) {
                    $("#id_is_lead").prop("checked", true);
                    $("#id_is_lead").prop("disabled", true);
                } else {
                    $("#id_is_lead").prop("checked", member.is_lead);
                    $("#id_is_lead").prop("disabled", false);
                }
                $("#id_active").prop("checked", member.active);
                $("#id_active").prop("disabled", false);
            }
            $('#memberModal').modal();
            $('#memberSaveBtn').off('click');
            $('#memberSaveBtn').click(function () {
                saveMemberDetails(id);
            });
        }, 'json');
    }

    $('button.edit-member').click(function () {
        memberDetails($(this).closest('tr').attr('data-id'));
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
            row.child("<div class='slidable' id='outer-box-"+id+"'></div>").show();
            renderBox('#outer-box-'+id, boxes[id].id);
            $('div.slidable', row.child()).slideDown();
            btn.text("Hide");
        }
    });

    let boxList = [];
    for(var id in boxes) {
        boxList.push(boxes[id]);
    }
    setupBoxes(boxList);

});
