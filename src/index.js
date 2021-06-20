require('bootstrap');
require('smartmenus');
require('smartmenus-bootstrap-4');
require('./modernizr');
require('datatables.net')

require('./modules/equipment');
require('./modules/unit-selector');
require('./pages/box');
require('./pages/memberlist');

import './styles/main.scss';
import $ from 'jquery';

require("bootstrap/dist/css/bootstrap.css");
require("./styles/jquery-ui.css");
require("smartmenus-bootstrap-4/jquery.smartmenus.bootstrap-4.css");
require("select2/dist/css/select2.css");
require("select2-theme-bootstrap4/dist/select2-bootstrap.css");
require("datatables.net-bs4/css/dataTables.bootstrap4.css");
require("datatables.net-bs4/js/dataTables.bootstrap4");
require("flatpickr/dist/flatpickr.css");

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
    flatpickr(".datetimefield", {
        enableTime: true,
        enableSeconds: true,
        dateFormat: "Y-m-d H:i:S",
    });
});


