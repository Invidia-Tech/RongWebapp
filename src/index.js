require('bootstrap');
require('smartmenus');
require('smartmenus-bootstrap-4');
require('./modernizr');
require('datatables.net')

require('./modules/equipment');
require('./modules/unit-selector');
require('./pages/box');
require('./pages/memberlist');
require('./pages/hit-log');

import './styles/main.scss';
import $ from 'jquery';

require("bootstrap/dist/css/bootstrap.css");
require("./styles/jquery-ui.css");
require("smartmenus-bootstrap-4/jquery.smartmenus.bootstrap-4.css");
require("select2/dist/css/select2.css");
require("select2-theme-bootstrap4/dist/select2-bootstrap.css");
require("datatables.net-bs4/css/dataTables.bootstrap4.css");
require("datatables.net-bs4/js/dataTables.bootstrap4");
require("datatables.net-rowreorder-bs4/css/rowReorder.bootstrap4.css");
require("flatpickr/dist/flatpickr.css");
require("font-awesome/css/font-awesome.css");

const flatpickr = require("flatpickr").default;

$(document).ready(function () {
    $(".dt").each(function () {
        let $t = $(this);
        let opt = {};
        if ($t.hasClass('dt-noPaging')) {
            opt.paging = false;
        }
        $t.DataTable(opt);
    });
    $(".datetimefield").each(function () {
        let dtfield = this;
        let clearButton = $("<button type='button' class='btn btn-outline-danger'><i class=\"fa fa-close\"></i></button>");
        clearButton.click(function () {
            if (typeof dtfield._flatpickr !== "undefined") {
                dtfield._flatpickr.clear();
            } else {
                $(dtfield).val('');
            }
        });
        $(this).parent().addClass("input-group").append($("<span class='input-group-append'></span>").append(clearButton));
    });
    flatpickr(".datetimefield", {
        enableTime: true,
        enableSeconds: true,
        dateFormat: "Y-m-d H:i:S",
    });

    // workaround for https://github.com/select2/select2/issues/5993
    $(document).on("select2:open", () => {
        document.querySelector(".select2-container--open .select2-search__field").focus();
    });

    $('.select2-dd').select2({
        theme: 'bootstrap',
        placeholder: "Select...",
        allowClear: true
    });
});


