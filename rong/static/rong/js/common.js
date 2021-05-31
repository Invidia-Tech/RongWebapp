function rank_color(rank) {
    rank_num = parseInt(rank);
    if (isNaN(rank_num)) {
        return 'white';
    }
    if (rank_num < 0 || rank_num > 14) {
        return 'white';
    }
    return ['white', 'blue', 'bronze', 'bronze', 'silver', 'silver', 'silver', 'gold', 'gold', 'gold', 'gold', 'purple', 'purple', 'purple', 'purple'][rank_num];
}

function icon_id(unit_id, star) {
    star_num = parseInt(star);
    if (star_num < 3 || star_num > 5) {
        return Math.floor(unit_id / 100) * 100 + 11;
    }
    else {
        return Math.floor(unit_id / 100) * 100 + 31;
    }
}

function show_loading(text) {
    if (text) {
        $('.loading-spanner p').text(text);
    }
    $("div.loading-spanner").addClass("show");
    $("div.loading-overlay").addClass("show");
}

function hide_loading() {
    $("div.loading-spanner").removeClass("show");
    $("div.loading-overlay").removeClass("show");
}

function unit_position(range) {
    if (range < 300) {
        return 'front';
    }
    else if (range < 600) {
        return 'middle';
    }
    else {
        return 'back';
    }
}

function make_alert(dest, type, text) {
    let alertBox = $('<div class="alert alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="close">&#215;</button><span class="alert-text"></span></div>');
    alertBox.addClass('alert-'+type);
    alertBox.find('.alert-text').text(text);
    dest.prepend(alertBox);
    setTimeout(function() {
        alertBox.fadeOut(1000);
    }, 5000);
}

function equipment_stars(promotion_level) {
    if(promotion_level >= 4) {
        return 5;
    }
    else if(promotion_level == 3) {
        return 3;
    }
    else if(promotion_level == 2) {
        return 1;
    }
    else {
        return 0;
    }
}

function populateNumericDropdown(id, min, max, value) {
    let select_el = $('#' + id);
    select_el.empty();
    for (let choice = min; choice <= max; choice++) {
        select_el.append($("<option></option>").attr("value", choice).text(choice));
    }
    select_el.val(value);
}
