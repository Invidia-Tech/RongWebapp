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
require('./pages/edit-battle');
require('./pages/box-summary');
require('./pages/box-summary-unitfilter');
require('./pages/dashboard');

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
require("datatables.net-fixedcolumns-bs4/css/fixedColumns.bootstrap4.css");
require("flatpickr/dist/flatpickr.css");
require("font-awesome/css/font-awesome.css");

const flatpickr = require("flatpickr").default;

$.fn.outerHTML = function () {
    return $(this).clone().wrap('<div></div>').parent().html();
};

$.fn.hasAttr = function (name) {
    let attr = this.attr(name);
    return typeof attr !== 'undefined' && attr !== false;
};

$(document).ready(function () {
    $(".transition-delay").each(function (index, element) {
        setTimeout(function () { $(element).removeClass("transition-delay") }, 10);
    });
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

    $('.select2-dd').each(function () {
        $(this).select2({
            theme: 'bootstrap',
            placeholder: $(this).hasAttr("placeholder") ? $(this).attr("placeholder") : "Select...",
            allowClear: true
        });
    });

    $('.select2-multi').select2({
        theme: 'bootstrap'
    });

    // Javascript to enable link to tab
    var url = document.location.toString();
    if (url.match('#')) {
        $('.nav-tabs a[href="\\#' + url.split('#')[1] + '"]').tab('show');
    }

    // With HTML5 history API, we can easily prevent scrolling!
    $('.nav-tabs a').on('shown.bs.tab', function (e) {
        if (history.pushState) {
            history.pushState(null, null, e.target.hash);
        } else {
            window.location.hash = e.target.hash; //Polyfill for old browsers
        }
    })
});


