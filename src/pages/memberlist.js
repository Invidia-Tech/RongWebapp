import $ from 'jquery';
import {formatDiscordName, formatPlayerId, hide_loading, make_alert, show_loading} from '../modules/common';
import 'jquery-validation';
import 'jquery-mask-plugin';

$(document).ready(function () {
    if ($('.clan_list_members')) {
        let $api = $('.api');

        function saveMemberDetails(id) {
            $('#editMemberForm').validate();
            if ($('#editMemberForm').valid()) {
                $('#editMemberModal').modal('hide');
                $("#id_player_id").unmask();
                show_loading();
                $.post($api.attr('data-api-url') + "/" + id, $('#editMemberForm').serialize(), function (data) {
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
            $.get($api.attr('data-api-url') + "/" + id, function (member) {
                hide_loading();
                $("#editMemberName .name").text(member.name);
                $("#editMemberName .discriminator").text("#" + member.discriminator.toString().padStart(4, "0"));
                $("#id_ign").val(member.ign ?? "");
                $("#id_player_id").val(member.player_id ?? "");
                $("#id_player_id").mask('000 000 000');
                $("#id_group_num").val(member.group_num ?? "");
                if ($("#id_is_lead").length) {
                    $("#id_is_lead").prop("checked", member.is_lead);
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
        })
    }
});
