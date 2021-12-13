import $ from 'jquery';
import {formatDiscordName, formatPlayerId, hide_loading, make_alert, page, show_loading} from '../modules/common';
import 'jquery-validation';
import 'jquery-mask-plugin';
import {renderBox, setupBoxes, boxes as editorBoxes} from "../modules/box-editing";

require("datatables.net-bs4/js/dataTables.bootstrap4");

page('clan_list_members', function () {
    let $api = $('.api');
    let boxes = JSON.parse(document.getElementById('boxData').textContent);

    function createMemberRow(data) {
        let newTableID = data.member.active ? '#memberListTable' : '#memberListInactiveTable';
        let newRow = "";
        if (data.member.active) {
            newRow = "<tr data-id=\"" + data.member.id + "\">\n" +
                "                <td class=\"member-ign\"></td>\n" +
                "                <td class=\"member-discord\"></td>\n" +
                "                <td class=\"member-pid\"></td>\n" +
                "                <td class=\"member-lead\"></td>\n" +
                "                <td>\n" +
                "                    <button type=\"button\" class=\"btn btn-primary show-member-box\">Show</button>\n" +
                "                </td>\n" +
                "                <td class=\"member-box-update\" data-sort='"+data.member.box.last_update_unixtime+"'></td>\n" +
                "                <td>\n" +
                "                    <button type=\"button\" class=\"btn btn-primary edit-member\">Edit Details</button>\n" +
                "                </td>\n" +
                "            </tr>";
        } else {
            newRow = "<tr data-id=\"" + data.member.id + "\">\n" +
                "                <td class=\"member-ign\"></td>\n" +
                "                <td class=\"member-discord\"></td>\n" +
                "                <td class=\"member-pid\"></td>\n" +
                "                <td>\n" +
                "                    <button type=\"button\" class=\"btn btn-primary edit-member\">Edit Details</button>\n" +
                "                </td>\n" +
                "            </tr>";
        }
        $(newTableID).DataTable().row.add($(newRow)).draw();
        attachButtonEvents();
    }

    function populateMemberRow(data) {
        let $rootRow = $("tr[data-id='" + data.member.id + "'");
        if (data.member.discord_id) {
            $rootRow.find(".member-discord").html(formatDiscordName(data.member.discord_username, data.member.discord_discriminator));
        } else {
            $rootRow.find(".member-discord").html('N/A');
        }
        $rootRow.find(".member-ign").text(data.member.ign);
        $rootRow.find(".member-pid").text(formatPlayerId(data.member.player_id));
        if (data.member.is_admin) {
            $rootRow.find(".member-lead").text("Admin");
        } else {
            $rootRow.find(".member-lead").text(data.member.is_lead ? "Yes" : "No");
        }
        $rootRow.find(".member-box-update").text(data.member.box.last_update);
        $rootRow.parents('table').DataTable().rows().invalidate('dom').draw();
    }

    function saveMemberDetails(id) {
        $('#memberForm').validate();
        if ($('#memberForm').valid()) {
            $('#memberModal').modal('hide');
            $("#id_player_id").unmask();
            show_loading();
            $.post($api.attr('data-api-url') + id + "/", $('#memberForm').serialize(), function (data) {
                if (data.success) {
                    let $rootRow = $("tr[data-id='" + data.member.id + "'");
                    let rootTable = $rootRow.parents('table');
                    let expectedActive = rootTable.prop("id") === 'memberListTable';
                    if (expectedActive !== data.member.active) {
                        let oldTable = rootTable.DataTable();
                        oldTable.row($rootRow).remove().draw();
                        createMemberRow(data);
                    }
                    populateMemberRow(data);
                    make_alert($('#mainContent'), 'success', 'Member details edited successfully.');
                } else {
                    make_alert($('#mainContent'), 'danger', 'Could not edit member details.');
                }
                hide_loading();
            });
        }
    }

    function doAddMember() {
        $('#memberForm').validate();
        if ($('#memberForm').valid()) {
            $('#memberModal').modal('hide');
            $("#id_player_id").unmask();
            show_loading();
            $.post($api.attr('data-api-url') + "add/", $('#memberForm').serialize(), function (data) {
                if (data.success) {
                    boxes[data.member.id] = data.member.box;
                    editorBoxes[data.member.box.id] = data.member.box;
                    createMemberRow(data);
                    populateMemberRow(data);
                    make_alert($('#mainContent'), 'success', 'Added new member successfully.');
                } else {
                    make_alert($('#mainContent'), 'danger', 'Could not add new member.');
                }
                hide_loading();
            });
        }
    }

    function editMemberDetails(id) {
        show_loading();
        $.get($api.attr('data-api-url') + id + "/", function (member) {
            hide_loading();
            $("#id_ign").val(member.ign ?? "");
            $("#id_player_id").val(member.player_id ? formatPlayerId(member.player_id) : "");
            $("#id_player_id").mask('000 000 000');
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
            $('#memberModalLabel').text('Edit Member Details');
            $('#memberModal').modal();
            $('#memberSaveBtn').off('click').click(function () {
                saveMemberDetails(id);
            });
        }, 'json');
    }

    function addMember() {
        $("#id_ign").val("");
        $("#id_player_id").val("");
        $("#id_player_id").mask('000 000 000');
        $("#id_discord").val("");
        if ($("#id_is_lead").length) {
            $("#id_is_lead").prop("checked", false);
            $("#id_is_lead").prop("disabled", false);
            $("#id_active").prop("checked", true);
            $("#id_active").prop("disabled", false);
        }
        $('#memberModal').modal();
        $('#memberModalLabel').text('Add Member');
        $('#memberSaveBtn').off('click').click(function () {
            doAddMember();
        });
    }

    function attachButtonEvents() {
        $('button.edit-member').off('click').click(function () {
            editMemberDetails($(this).closest('tr').attr('data-id'));
        });

        $('button.show-member-box').off('click').click(function () {
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
                row.child("<div class='slidable' id='outer-box-" + id + "'></div>").show();
                renderBox('#outer-box-' + id, boxes[id].id);
                $('div.slidable', row.child()).slideDown();
                btn.text("Hide");
            }
        });
    }


    let boxList = [];
    for (var id in boxes) {
        boxList.push(boxes[id]);
    }
    setupBoxes(boxList);
    attachButtonEvents();

    $('#addMemberBtn').click(addMember);

});
