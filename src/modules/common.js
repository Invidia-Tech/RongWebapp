import $ from 'jquery';
import {equipmentData} from "./equipment";

export function rank_color(rank) {
    let rank_num = parseInt(rank);
    if (isNaN(rank_num)) {
        return 'white';
    }
    if (rank_num < 0 || rank_num > 17) {
        return 'white';
    }
    return ['white', 'blue', 'bronze', 'bronze', 'silver', 'silver', 'silver', 'gold', 'gold', 'gold', 'gold', 'purple', 'purple', 'purple', 'purple', 'purple', 'purple', 'purple'][rank_num];
}

export function icon_id(unit_id, star) {
    let star_num = parseInt(star);
    if (star_num < 3 || star_num > 6) {
        return Math.floor(unit_id / 100) * 100 + 11;
    } else if (star_num == 6) {
        return Math.floor(unit_id / 100) * 100 + 61;
    } else {
        return Math.floor(unit_id / 100) * 100 + 31;
    }
}

export function show_loading(text) {
    if (text) {
        $('.loading-spanner p').text(text);
    }
    $("div.loading-spanner").addClass("show");
    $("div.loading-overlay").addClass("show");
}

export function hide_loading() {
    $("div.loading-spanner").removeClass("show");
    $("div.loading-overlay").removeClass("show");
}

export function unit_position(range) {
    if (range < 300) {
        return 'front';
    } else if (range < 600) {
        return 'middle';
    } else {
        return 'back';
    }
}

export function make_alert(dest, type, text) {
    let alertBox = $('<div class="alert alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="close">&#215;</button><span class="alert-text"></span></div>');
    alertBox.addClass('alert-' + type);
    alertBox.find('.alert-text').text(text);
    dest.prepend(alertBox);
    setTimeout(function () {
        alertBox.fadeOut(1000);
    }, 5000);
}

export function equipment_stars(promotion_level) {
    if (promotion_level >= 4) {
        return 5;
    } else if (promotion_level == 3) {
        return 3;
    } else if (promotion_level == 2) {
        return 1;
    } else {
        return 0;
    }
}

export function populateNumericDropdown(id, min, max, value) {
    let select_el = $('#' + id);
    select_el.empty();
    for (let choice = min; choice <= max; choice++) {
        select_el.append($("<option></option>").attr("value", choice).text(choice));
    }
    select_el.val(value);
}

export function formatDiscordName(name, discriminator) {
    let $template = $("<span><span class='name'></span><span class='discriminator'></span></span>");
    $template.find(".name").text(name);
    $template.find(".discriminator").text("#" + discriminator.toString().padStart(4, "0"));
    return $template.html();
}

export function formatPlayerId(id) {
    if (!id) {
        return "N/A";
    }
    let rawId = id.toString().padStart(9, "0");
    return rawId.substr(0, 3) + " " + rawId.substr(3, 3) + " " + rawId.substr(6, 3);
}

export function page(name, cb) {
    $(document).ready(function () {
        if ($('.page__' + name).length) {
            cb();
        }
    });
}

export function getDescendantProp(obj, desc) {
    var arr = desc.split(".");
    while (arr.length && (obj = obj[arr.shift()])) ;
    return obj;
}

export function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

export function rankDesc(unit, box_unit) {
    let text = "R" + box_unit.rank + "-";
    let numEquips = 0;
    let equipLevel = [-1, -1, -1, -1, -1, -1];
    let levelMaxes = [0, 0, 0, 0, 0, 0];
    let pieceNames = ["TL", "TR", "ML", "MR", "BL", "BR"];
    let allFilledMax = true;
    for (let i = 0; i < 6; i++) {
        equipLevel[i] = (box_unit["equip" + (i + 1)] !== null) ? box_unit["equip" + (i + 1)] : -1;
        let eq_id = unit.ranks[box_unit.rank - 1][i].toString();
        levelMaxes[i] = eq_id === "999999" ? -1 : equipment_stars(equipmentData[eq_id].promotion_level);
        numEquips += (equipLevel[i] >= 0) ? 1 : 0;
        if (equipLevel[i] >= 0 && equipLevel[i] < levelMaxes[i]) {
            allFilledMax = false;
        }
    }
    text += numEquips;
    let equipDesc = "";
    if (numEquips < 3 || (numEquips < 4 && equipLevel[4] >= 0) || (numEquips < 5 && equipLevel[2] >= 0) || (numEquips < 6 && equipLevel[0] >= 0) || !allFilledMax) {
        // specify each piece
        for (let i = 0; i < 6; i++) {
            if (equipLevel[i] >= 0) {
                equipDesc += " " + pieceNames[i] + equipLevel[i];
            }
        }
    }
    if (equipDesc !== "") {
        return "<span class='underline-dotted' title='" + equipDesc.substring(1) + "'>" + text + "</span>";
    }
    return text;
}
