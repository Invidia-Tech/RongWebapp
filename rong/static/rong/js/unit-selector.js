(function ($) {

    $.fn.extend({
        unitselector: function (options) {
            options = $.extend({}, $.UnitSelector.defaults, options);

            this.each(function () {
                new $.UnitSelector(this, options);
            });
            return this;
        },
        unitselectormulti: function (options) {
            options = $.extend({}, $.UnitSelectorMulti.defaults, options);

            this.each(function () {
                new $.UnitSelectorMulti(this, options);
            });
            return this;
        }
    });

    function formatState(state) {
        if (!state.id) {
            return state.text;
        }

        let $state = $(
            '<div class="unit-dropdown-item"><div class="unit-ddicon"></div> <span></span></div>'
        );

        // Use .text() instead of HTML string concatenation to avoid script injection issues
        $state.find("span").text(state.text);
        $state.find("div.unit-ddicon").addClass("u-" + icon_id(parseInt(state.element.value), 3));

        return $state;
    }

    // @TODO load real nicknames from rongbot db
    let nicknames = [];

    function matchCustom(params, data) {
        // If there are no search terms, return all of the data
        if ($.trim(params.term) === '') {
            return data;
        }

        // Do not display the item if there is no 'text' property
        if (typeof data.text === 'undefined') {
            return null;
        }

        // `params.term` should be the term that is used for searching
        // `data.text` is the text that is displayed for the data object
        if (data.text.toUpperCase().indexOf(params.term.toUpperCase()) > -1) {
            return data;
        }

        for (const nickname of nicknames) {
            if (data.element.value === nickname.unit && nickname.name.toUpperCase().indexOf(params.term.toUpperCase()) > -1) {
                let modifiedData = $.extend({}, data, true);
                modifiedData.text += ' (' + nickname.name + ')';

                // You can return modified objects from here
                // This includes matching the `children` how you want in nested data sets
                return modifiedData;
            }
        }

        // Return `null` if the term should not be displayed
        return null;
    }

    // ctl is the element, options is the set of defaults + user options
    $.UnitSelector = function (ctl, options) {
        $(ctl).select2({
            theme: 'bootstrap4',
            templateSelection: formatState,
            templateResult: formatState,
            matcher: matchCustom
        });
    };

    // option defaults
    $.UnitSelector.defaults = {};

    $.UnitSelectorMulti = function (ctl, options) {
        $(ctl).select2({
            templateResult: formatState,
            maximumSelectionLength: 5,
            matcher: matchCustom
        });
    };

    // option defaults
    $.UnitSelectorMulti.defaults = {};

    $(document).ready(function() {
        if($("#unitNicknames").length > 0) {
            nicknames = JSON.parse(document.getElementById('unitNicknames').textContent);
        }
    });

})(jQuery);