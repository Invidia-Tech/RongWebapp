import $ from 'jquery';
import {page, show_loading} from '../modules/common';
import 'jquery-validation';
import 'datatables.net';
import 'datatables.net-rowreorder';

page('cb_list_hits', function () {
    let table = $('#hitLogTable').DataTable({
        columnDefs: [
            { orderable: false, targets: 0 }
        ],
        order: [[1, "desc"]],
        rowReorder: {
            selector: 'span.grippy',
            dataSrc: 1,
        }
    });
    table.on('row-reorder', function(e, diff, edit) {
        let reorderData = {};
        diff.forEach(function(change) {
            reorderData[$(change.node).attr("data-id")] = change.newData;
        })
        show_loading();
        $('#reorderData').val(JSON.stringify(reorderData));
        $('#reorderForm').submit();
    });
});

