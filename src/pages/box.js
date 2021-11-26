import $ from 'jquery';
import {hide_loading, make_alert, page, show_loading} from '../modules/common';
import {boxes, renderBoxes, setupBoxes} from "../modules/box-editing";
import 'jquery-validation';

page('box_index', function () {

    function doCreateBox() {
        $('#boxForm').validate();
        if ($('#boxForm').valid()) {
            $('#boxModal').modal('hide');
            show_loading();
            $.post("/box/create/", $('#boxForm').serialize(), function (data) {
                if (data.success) {
                    boxes[data.box.id] = data.box;
                    renderBoxes();
                    make_alert($('#mainContent'), 'success', 'Box created successfully.');
                } else {
                    make_alert($('#mainContent'), 'danger', 'Could not create box.');
                }
                hide_loading();
            });
        }
    }

    function createBox() {
        $('#boxModalLabel').text('Create Box');
        $('#boxNameField').val("");
        $('#boxSaveBtn').off('click');
        $('#boxSaveBtn').click(doCreateBox);
        $('#boxModal').modal();
    }

    $('#createBoxBtn').click(createBox);

    setupBoxes(JSON.parse(document.getElementById('boxData').textContent));
    renderBoxes();
});
