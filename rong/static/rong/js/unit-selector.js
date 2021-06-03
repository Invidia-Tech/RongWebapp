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
        if (typeof (state.text) == "string") {
            $state.find("span").text(state.text);
        } else {
            $state.find("span").append(state.text);
        }
        $state.find("div.unit-ddicon").addClass("u-" + icon_id(parseInt(state.element.value), 3));

        return $state;
    }

    // load nicknames from page, if provided
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
        let matchName = data.text.toUpperCase().indexOf(params.term.toUpperCase());
        if (matchName > -1) {
            // let modifiedData = $.extend({}, data, true);
            // let highlightedText = $('<span><span></span><b></b><span></span></span>');
            // highlightedText.find("span:first-child").text(data.text.substr(0, matchName));
            // highlightedText.find("b").text(data.text.substr(matchName, params.term.length));
            // highlightedText.find("span:last-child").text(data.text.substr(matchName + params.term.length));
            // modifiedData.text = highlightedText;
            // return modifiedData;
            return data;
        }

        for (const nickname of nicknames) {
            let matchNick = nickname.name.toUpperCase().indexOf(params.term.toUpperCase());
            if (data.element.value === nickname.unit && matchNick > -1) {
                let modifiedData = $.extend({}, data, true);
                // uncomment the below to enable search highlighting
                // let highlightedText = $('<span><span></span><b></b><span></span></span>');
                // highlightedText.find("span:first-child").text(data.text.toString() + ' [' + nickname.name.substr(0, matchNick));
                // highlightedText.find("b").text(nickname.name.substr(matchNick, params.term.length));
                // highlightedText.find("span:last-child").text(nickname.name.substr(matchNick + params.term.length) + ']');
                // modifiedData.text = highlightedText;
                modifiedData.text += ' [' + nickname.name + ']';
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
            matcher: matchCustom,
            placeholder: "Select...",
            allowClear: true
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

    $(document).ready(function () {
        if ($("#unitNicknames").length > 0) {
            nicknames = JSON.parse(document.getElementById('unitNicknames').textContent);
        }
    });

})(jQuery);