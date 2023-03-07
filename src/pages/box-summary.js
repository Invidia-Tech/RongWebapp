import $ from 'jquery';
import {icon_id, page, rankDesc} from '../modules/common';
import 'jquery-validation';
import 'jquery-mask-plugin';

require("datatables.net-bs4/js/dataTables.bootstrap4");
import 'datatables.net-fixedcolumns';

page('clan_box_summary', function () {
    let members = JSON.parse(document.getElementById('memberData').textContent);
    for (let member of members) {
        const box_data = member.box.units;
        for (const uid in box_data) {
            const unit = box_data[uid];
            member["unit_" + unit.unit_id] = unit;
        }
    }
    let units = JSON.parse(document.getElementById('unitData').textContent);
    let columns = [];
    columns.push({title: "Name", data: "ign", className: "unit-viewer-name-column"});
    for (let unit of units) {
        let unit_el = $("<div class='unit-icon'></div>").addClass('u-' + icon_id(unit.id, unit.rarity));
        unit_el.attr('title', unit.name);
        columns.push({
            title: unit_el.outerHTML(),
            data: "unit_" + unit["id"],
            width: "100px",
            defaultContent: "",
            render: function (data, type) {
                if (type === 'display') {
                    if (data === undefined) {
                        return "N/A";
                    }
                    let ue = "";
                    if (data.max_ue_level > -1) {
                        if (data.ue_level === null) {
                            ue = "<br />No UE";
                        } else {
                            ue = "<br />UE" + data.ue_level;
                        }
                    }
                    let slvl_info = "";
                    for (let slvl of ["ub_level", "s1_level", "s2_level", "ex_level"]) {
                        if (data[slvl] !== null && data[slvl] !== data.level) {
                            slvl_info += " " + slvl.substring(0, 2).toUpperCase() + "@" + data[slvl];
                        }
                    }
                    let level = "Lv" + data.level.toString();
                    if (slvl_info !== "") {
                        level = "<span class='underline-dotted' title='" + slvl_info.substring(1) + "'>" + level + "</span>";
                    }
                    let retval = data.star + "★ " + rankDesc(unit, data) + "<br />" + level + ue + "<br/>Bond" + data.bond;
                    if (data.power !== null) {
                        retval += "<br/>Power: " + data.power;
                    }
                    return retval;
                } else {
                    if (data === undefined) {
                        return 0;
                    }
                    let eq_count = 0;
                    for (let i = 1; i <= 6; i++) {
                        if (data["equip" + i] !== null) {
                            eq_count++;
                        }
                    }
                    let ue_lvl = (data.ue_level === null) ? 0 : data.ue_level;
                    return (
                        data.level
                        + ue_lvl * 1000
                        + eq_count * 1000000
                        + data.rank * 10000000
                        + data.star * 1000000000
                    );
                }
            }
        });
    }
    let storedFilter = window.localStorage.getItem('unitFilter');
    let unitFilter;
    if (storedFilter === null) {
        unitFilter = [];
        for (const unit of units) {
            unitFilter.push(unit.id);
        }
    } else {
        unitFilter = JSON.parse(storedFilter);
    }
    let table = $('#boxSummaryTable').DataTable({
        data: members,
        columns: columns,
        paging: false,
        scrollY: "70vh",
        scrollX: true,
        autoWidth: false,
        fixedColumns: true
    });

    let unitData = [];
    for (const unit of units) {
        let unitRow = [unit.name, 0, 0, 0, 0, 0, 0, 0, 0];
        for (const member of members) {
            if (member.hasOwnProperty("unit_" + unit.id)) {
                unitRow[member["unit_" + unit.id]["star"] + 1] += 1;
                unitRow[8] += 1;
            } else {
                unitRow[1] += 1;
            }
        }
        unitData.push(unitRow);
    }

    $('#unitCountsTable').DataTable({
        data: unitData,
        paging: false
    });

    function applyUnitFilter() {
        for (let idx = 0; idx < units.length; idx++) {
            let unit = units[idx];
            let column = table.column(idx + 1);
            let active = unitFilter.includes(unit.id);
            column.visible(active, false);
            $('#unitSelect-' + unit.id).toggleClass('inactive', !active);
        }
        table.draw();
        window.localStorage.setItem('unitFilter', JSON.stringify(unitFilter));
    }

    function toggleUnit(id) {
        const idx = unitFilter.indexOf(id);
        if (idx > -1) {
            // remove
            unitFilter.splice(idx, 1);
        } else {
            unitFilter.push(id);
        }
        applyUnitFilter();
    }

    applyUnitFilter();

    $('#selectUnitsBtn').click(function () {
        $('#unitSelectorUnits').empty();
        for (const unit of units) {
            let unit_el = $("<div class='unit-ddicon unit-selector-icon'></div>").addClass('u-' + icon_id(unit.id, unit.rarity));
            unit_el.attr('title', unit.name);
            unit_el.toggleClass('inactive', !unitFilter.includes(unit.id));
            unit_el.attr('id', 'unitSelect-' + unit.id);
            unit_el.click(function () {
                toggleUnit(unit.id);
            });
            unit_el.appendTo('#unitSelectorUnits');
        }
        $('#unitSelectorModal').modal();
    });
    $('#selectAllBtn').click(function () {
        unitFilter = [];
        for (const unit of units) {
            unitFilter.push(unit.id);
        }
        applyUnitFilter();
    });
    $('#selectNoneBtn').click(function () {
        unitFilter = [];
        applyUnitFilter();
    });

    // adds `/` shortcut to open unit filter
    document.addEventListener('keydown', e => {
        // Wrong key
        if (e.key !== '/') return;

        // Already open
        const modal = document.querySelector("#unitSelectorModal.show");
        if (modal) return;

        e.preventDefault();
        document.querySelector("#selectUnitsBtn").click();
    });

    // filterUnits takes a filterText and returns array of elements matching the rules
    const filterUnits = filterText => {
        // If last character is `$` we use `$=` instead of `*=`
        const mode = (filterText.substr(-1) === "$") ? "$" : "*";
        filterText = (filterText.substr(-1) === "$") ? filterText.slice(0, -1) : filterText;

        return Array.from(document.querySelectorAll(`.unit-selector-icon[title${mode}="${filterText}"i]`));
    }

    // highlightUnits highlights all units matching `filterText`
    const highlightUnits = filterText => {
        // If it's empty do not highlight anything
        const parent = document.querySelector("#unitSelectorBody");
        if (filterText === "") {
            parent.classList.remove("highlighting");
        } else {
            parent.classList.add("highlighting");
        }

        // Remove previous highlights
        const highlighted = Array.from(document.querySelectorAll(".unit-selector-icon.highlight"));
        highlighted.forEach(el => el.classList.remove("highlight"));

        // Add new
        filterUnits(filterText).forEach(el => el.classList.add("highlight"));
    }

    // toggleUnits toggles all unit matching `filterText`
    const toggleUnits = filterText => {
        filterUnits(filterText).forEach(el => el.click());
    }

    $("#unitSelectorFilter").keyup(e => {
        if (e.keyCode == "13") {
            toggleUnits(e.target.value);
            e.target.value = "";
        }
        highlightUnits(e.target.value);
    });

});
