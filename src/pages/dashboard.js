import $ from 'jquery';
import {escapeHtml, page} from '../modules/common';
import 'jquery-validation';
import 'jquery-mask-plugin';

require("datatables.net-bs4/js/dataTables.bootstrap4");

page('cb_view', function () {
    if (document.getElementById('compStats')) {
        function renderComp(id) {
            let dtHits = $("#compHitsTable").DataTable();
            dtHits.clear();
            let compData = comps[id];
            for (let i = 0; i < compData.hits.length; i++) {
                let hit = compData.hits[i];
                let newRow = "<tr>" +
                    "<td>" + (i + 1) + "</td>" +
                    "<td>" + escapeHtml(hit.player) + "</td>" +
                    "<td>" + hit.lap + "</td>" +
                    "<td>" + hit.damage.toLocaleString() + "</td>" +
                    "<td>" + Math.round(hit.score) + "</td></tr>";
                dtHits.row.add($(newRow));
            }
            $("#compStatsMean").text(Math.round(compData.mean).toLocaleString());
            $("#compStatsMinimum").text(Math.round(compData.minimum).toLocaleString());
            $("#compStatsLQ").text(Math.round(compData.lower_quartile).toLocaleString());
            $("#compStatsMedian").text(Math.round(compData.median).toLocaleString());
            $("#compStatsUQ").text(Math.round(compData.upper_quartile).toLocaleString());
            $("#compStatsMaximum").text(Math.round(compData.maximum).toLocaleString());
            let dtHitters = $("#compHittersTable").DataTable();
            dtHitters.clear();
            for(let i=0; i < compData.player_info.length; i++) {
                let player = compData.player_info[i];
                let newRow = "<tr>"+
                    "<td>"+escapeHtml(player.name)+"</td>"+
                    "<td>"+player.count.toLocaleString()+"</td>"+
                    "<td>"+Math.round(player.mean).toLocaleString()+"</td>"+
                    "<td>"+Math.round(player.median).toLocaleString()+"</td>"+
                    "<td>"+Math.round(player.average_score)+"</td></tr>";
                dtHitters.row.add($(newRow));
            }
            dtHits.draw();
            dtHitters.draw();
        }

        let comps = JSON.parse(document.getElementById('compStats').textContent);
        let selector = $("#compStatsSelector");
        for (let i = 0; i < comps.length; i++) {
            selector.append("<option value='" + i + "'>" + escapeHtml(comps[i].comp) + "</option>");
        }
        selector.change(function() {
            renderComp(selector.val());
        })
        setTimeout(renderComp, 500, 0);
    }

});
