// Globals
var tournament = null;
var nav_index = 0;
var registration_type = 0; // 0 for single-line registration, 1 for bulk edit

function render_header() {
    // render name
    $("#tournament_name").text(tournament.name);

    // render status
    if (tournament.status == 0) {
        $("#tournament_status").html(
            "<span class='badge text-bg-secondary'>Open for registration</span>"
        );
    } else if (tournament.status == 1) {
        $("#tournament_status").html(
            "<span class='badge text-bg-success'>Running</span>"
        );
    } else {
        $("#tournament_status").html(
            "<span class='badge text-bg-primary'>Closed</span>"
        );
    }
}

function render_main() {
    if (tournament.status == 0) {
        render_main_registration();
    } else if (tournament.status == 1 && is_authenticated) {
        render_main_ongoing(true);
    } else {
        render_main_ongoing(false);
    }

    feather.replace({ height: 16, width: 16 });
}

function feather_icon(name) {
    return $("<i>").attr("height", "16").attr("data-feather", name);
}

function render_player_list(table_id) {
    if (tournament.players.length > 0) {
        tournament.players.map(function (e, index) {
            $(table_id)
                .find("tbody")
                .append(
                    $("<tr>")
                        .append($("<td>").addClass("text-muted").text(index + 1))
                        .append($("<td>").text(e.name))
                        .append(
                            $("<td>").append(
                                $("<button>")
                                    .attr("class", "btn btn-outline-danger btn-sm")
                                    .attr("title", "Remove")
                                    .append(feather_icon("x"))
                                    .click(function () {
                                        $.ajax({
                                            url: "/api/v1/tournaments/" + tournament.id + "/add/",
                                            headers: { Authorization: "Token " + auth_token },
                                            method: "DELETE",
                                            contentType: "application/json",
                                            data: JSON.stringify({ player: { name: e.name } }),
                                            success: function () { update_tournament_detail(); },
                                            error: function (error) {
                                                console.log(error);
                                                showAPIAlert(error.responseText);
                                            },
                                        });
                                    })
                            )
                        )
                );
        });
    } else {
        $(table_id).find("tbody").append(
            $("<tr>").append(
                $("<td>").attr("colspan", "3").append(
                    $("<div>").addClass("empty-state").html(
                        '<i data-feather="users" width="32" height="32"></i><p>No players yet</p>'
                    )
                )
            )
        );
    }
}

function render_main_registration() {
    $("#main_ongoing").css("display", "none");
    $("#main_registration").css("display", "block");
    $("#tournament-list-table").find("tbody").empty();
    $("#input-playername").val("");

    // next phase button
    $("#next-phase-button")
        .attr("class", "btn btn-sm btn-success btn-action-primary")
        .html('<i data-feather="play"></i> Begin pairings');

    // toggle between single-line and bulk input
    $("#button-switch-to-textarea").empty();
    if (registration_type == 0) {
        $("#button-switch-to-textarea")
            .append(feather_icon("file-text"))
            .append($("<span>").text(" Bulk edit"))
            .click(function () {
                registration_type = 1;
                render_main();
            });
        $("#tournament-list-textarea-input-group").hide();
        $("#tournament-list-table").empty().append($("<thead>")).append($("<tbody>")).show();
        render_player_list("#tournament-list-table");
        $("#tournament-list-table").find("thead").empty().append(
            $("<tr>")
                .append($("<th>").attr("scope", "col").text("#"))
                .append($("<th>").attr("scope", "col").text("Player name"))
                .append($("<th>").attr("scope", "col").html(""))
        );
    } else {
        $("#button-switch-to-textarea")
            .append(feather_icon("list"))
            .append($("<span>").text(" List view"))
            .click(function () {
                registration_type = 0;
                render_main();
            });
        $("#tournament-list-textarea-input-group").show();
        $("#tournament-list-table").empty().hide();
        var textarea_value = "";
        tournament.players.map(function (e) {
            textarea_value += e.name + "\n";
        });
        $("#tournament-list-textarea")
            .attr("rows", Math.max(tournament.players.length, 7))
            .val(textarea_value);
    }
}

function html_score(score, pod_id) {
    var primary = '<span class="fw-semibold">' + score[0] + '</span><small class="text-muted">pts</small>';
    var secondary = '<span class="fw-semibold">' + score[1] + '</span><small class="text-muted">tb</small>';
    if (pod_id === undefined) {
        return '<span class="score-display">' + primary + " &middot; " + secondary + "</span>";
    }
    if (pod_id == null) {
        return '<span class="badge text-bg-light">buy</span>';
    }
    return '<span class="score-display">' + primary + " &middot; " + secondary + "</span>";
}

function render_main_ongoing(is_running) {
    $("#tournament-list-table").empty();
    $("#main_ongoing").css("display", "block");
    $("#main_ongoing_body").empty();
    $("#ongoing_nav_list").empty();
    $("#button-new-round").css("display", "");
    $("#button-redo-pairings").css("display", "");
    $("#input-playername-div").css("display", "");

    if (!is_running) {
        $("#input-playername-div").css("display", "none");
        $("#button-new-round").css("display", "none");
        $("#button-redo-pairings").css("display", "none");
    }

    // next phase button
    if (tournament.status == 0) {
        $("#next-phase-button")
            .attr("class", "btn btn-sm btn-success btn-action-primary")
            .html('<i data-feather="check"></i> Close tournament');
    } else if (tournament.status == 1) {
        $("#next-phase-button")
            .attr("class", "btn btn-sm btn-primary btn-action-primary")
            .html('<i data-feather="lock"></i> Close tournament');
    } else {
        $("#next-phase-button")
            .attr("class", "btn btn-sm btn-outline-warning btn-action-primary")
            .html('<i data-feather="unlock"></i> Reopen');
    }

    // render round tabs
    $("#ongoing_nav_list").append(
        $("<a>")
            .attr("class", "round-tab" + (nav_index == 0 ? " active" : ""))
            .text("Standings")
            .click(function () {
                nav_index = 0;
                update_tournament_detail();
            })
    );
    for (var i = 0; i < tournament.rounds.n_rounds; i++) {
        var round_id = i + 1;
        $("#ongoing_nav_list").append(
            $("<a>")
                .attr("class", "round-tab" + (nav_index == round_id ? " active" : ""))
                .attr("data-page-index", round_id)
                .text("Round " + round_id)
                .click(function () {
                    nav_index = $(this).attr("data-page-index");
                    update_tournament_detail();
                })
        );
    }

    // render body
    if (nav_index == 0) {
        render_standings(is_running);
    } else {
        render_round_page(is_running);
    }
}

function render_standings(is_running) {
    var table = $("<table>")
        .attr("id", "table-player-list")
        .attr("class", "table table-sm standings-table");

    var header_row = $("<tr>")
        .append($("<th>").text("Player"))
        .append($("<th>").text("Status"))
        .append($("<th>").text("Total"));
    for (var i = 0; i < tournament.rounds.n_rounds; i++) {
        header_row.append($("<th>").text("R" + (i + 1)));
    }

    if (tournament.standings.length > 0) {
        table.append($("<thead>").append(header_row));
        var tbody = $("<tbody>");

        tournament.standings.map(function (e) {
            var row = $("<tr>")
                .append($("<td>").addClass("fw-medium").text(e.player_name))
                .append(
                    $("<td>").append(
                        (function () {
                            if (e.dropped) {
                                return $("<span>").addClass("badge text-bg-danger").text("dropped");
                            }
                            return $("<span>").addClass("badge text-bg-success").text("active");
                        })()
                    ).append(
                        (function () {
                            if (e.dropped || !is_running) return $("<span>");
                            return $("<button>")
                                .attr("class", "btn btn-outline-danger btn-sm ms-1")
                                .attr("title", "Drop player")
                                .css("padding", "0 .3rem")
                                .append(feather_icon("user-minus"))
                                .click(function () {
                                    $.ajax({
                                        url: "/api/v1/tournaments/" + tournament.id + "/drop/",
                                        headers: { Authorization: "Token " + auth_token },
                                        method: "POST",
                                        contentType: "application/json",
                                        data: JSON.stringify({ player: { name: e.player_name } }),
                                        success: function () { update_tournament_detail(); },
                                        error: function (error) {
                                            console.log(error);
                                            showAPIAlert(error.responseText);
                                        },
                                    });
                                });
                        })()
                    )
                )
                .append($("<td>").html(html_score(e.total_score)));

            e.rounds.map(function (rnd) {
                row.append($("<td>").html(html_score(rnd.score, rnd.pod_id)));
            });
            tbody.append(row);
        });
        table.append(tbody);
        $("#main_ongoing_body").append($("<div>").addClass("panel").append(table));
    } else {
        render_player_list("#table-player-list");
        $("#main_ongoing_body").append(
            $("<div>").addClass("panel").append(table)
        );
    }
}

function render_round_page(is_running) {
    var round_data = tournament.rounds.rounds[nav_index - 1];

    // Buys
    if (round_data.buys.length > 0) {
        var buys_badges = $("<div>").addClass("buys-list");
        round_data.buys.map(function (buy) {
            buys_badges.append(
                $("<span>").addClass("badge text-bg-light").text(buy)
            );
        });
        var buys_card = $("<div>").addClass("buys-card")
            .append($("<div>").addClass("buys-label").html('<i data-feather="coffee" height="14"></i> Byes'))
            .append(buys_badges);
        $("#main_ongoing_body").append(buys_card);
    }

    // Pods
    var pod_id = 0;
    round_data.pods.map(function (pod) {
        pod_id += 1;
        var card = $("<div>").addClass("pod-card");
        card.append($("<div>").addClass("pod-card-header").text("Pod " + pod_id));

        // Column labels
        card.append(
            $("<div>").addClass("pod-player-row").css("border-bottom", "none").css("padding-bottom", "0")
                .append($("<div>"))
                .append($("<div>").addClass("pod-score-label").text("Score"))
                .append($("<div>").addClass("pod-score-label").text("Tiebreak"))
        );

        for (var i = 0; i < pod.players.length; i++) {
            var player_name = pod.players[i];
            var player_score = pod.scores[i];

            var row = $("<div>").addClass("pod-player-row");
            row.append($("<div>").addClass("pod-player-name").text(player_name));

            // Primary score
            row.append(
                $("<input>")
                    .attr("type", "number")
                    .attr("class", "form-control form-control-sm pod-score-input")
                    .attr("data-player-name", player_name)
                    .attr("data-score-index", "0")
                    .prop("readonly", !is_running)
                    .val(player_score[0] != null ? player_score[0] : null)
                    .change(function () {
                        var val = $(this).val();
                        var name = $(this).attr("data-player-name");
                        $.ajax({
                            url: "/api/v1/tournaments/" + tournament.id + "/submit/",
                            headers: { Authorization: "Token " + auth_token },
                            method: "POST",
                            contentType: "application/json",
                            data: JSON.stringify({
                                player: { name: name },
                                round_id: nav_index - 1,
                                score: [parseInt(val), null],
                            }),
                            success: function () { console.log("Score updated"); },
                            error: function (error) {
                                console.log(error);
                                showAPIAlert(error.responseText);
                            },
                        });
                    })
            );

            // Secondary score
            row.append(
                $("<input>")
                    .attr("type", "number")
                    .attr("class", "form-control form-control-sm pod-score-input")
                    .attr("data-player-name", player_name)
                    .attr("data-score-index", "1")
                    .prop("readonly", !is_running)
                    .val(player_score[1] != null ? player_score[1] : null)
                    .change(function () {
                        var val = $(this).val();
                        var name = $(this).attr("data-player-name");
                        $.ajax({
                            url: "/api/v1/tournaments/" + tournament.id + "/submit/",
                            headers: { Authorization: "Token " + auth_token },
                            method: "POST",
                            contentType: "application/json",
                            data: JSON.stringify({
                                player: { name: name },
                                tournament: tournament.id,
                                round_id: nav_index - 1,
                                score: [null, parseInt(val)],
                            }),
                            success: function () { console.log("Score updated"); },
                            error: function (error) {
                                console.log(error);
                                showAPIAlert(error.responseText);
                            },
                        });
                    })
            );

            card.append(row);
        }
        $("#main_ongoing_body").append(card);
    });
}

function render_tournament_detail() {
    render_header();
    render_main();
}

function update_tournament_detail() {
    $.get({
        url: "/api/v1/tournaments/" + tournament_id + "/",
        headers: get_request_headers(),
        success: function (result) {
            tournament = result;
            render_tournament_detail();
        },
        error: function (error) {
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
}

$(document).ready(function () {
    update_tournament_detail();
});

$("#button-add").click(function () {
    $.post({
        url: "/api/v1/tournaments/" + tournament.id + "/add/",
        headers: get_request_headers(),
        contentType: "application/json",
        data: JSON.stringify({ player: { name: $("#input-playername").val() } }),
        success: function () {
            update_tournament_detail();
            $("#input-playername").val("").focus();
        },
        error: function (error) {
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

$("#next-phase-button").click(function () {
    var new_status = tournament.status < 2 ? tournament.status + 1 : 1;
    $.ajax({
        url: "/api/v1/tournaments/" + tournament.id + "/",
        headers: { Authorization: "Token " + auth_token },
        method: "PUT",
        contentType: "application/json",
        data: JSON.stringify({ status: new_status }),
        success: function () { update_tournament_detail(); },
        error: function (error) {
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

$("#button-new-round").click(function () {
    $.post({
        url: "/api/v1/tournaments/" + tournament.id + "/round/",
        headers: get_request_headers(),
        success: function (result) {
            nav_index = parseInt(result.rounds.n_rounds);
            update_tournament_detail();
        },
        error: function (error) {
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

$("#button-redo-pairings").click(function () {
    $.post({
        url: "/api/v1/tournaments/" + tournament.id + "/round/redo/",
        headers: get_request_headers(),
        success: function () {
            nav_index = parseInt(tournament.rounds.n_rounds);
            update_tournament_detail();
        },
        error: function (error) {
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

function parse_textarea_into_player_names() {
    var result = [];
    $("#tournament-list-textarea").val().split("\n").map(function (e) {
        if (e.trim().length > 0) {
            result.push({ name: e.trim() });
        }
    });
    return result;
}

$("#tournament-list-textarea-update").click(function () {
    $.post({
        url: "/api/v1/tournaments/" + tournament.id + "/bulk-edit/",
        headers: get_request_headers(),
        contentType: "application/json",
        data: JSON.stringify({ players: parse_textarea_into_player_names() }),
        success: function () {
            update_tournament_detail();
            $("#tournament-list-textarea").focus();
            $("#tournament-list-textarea-update")
                .removeClass("btn-primary").addClass("btn-success")
                .html('<i data-feather="check"></i> Updated');
            feather.replace({ height: 16, width: 16 });
            setTimeout(function () {
                $("#tournament-list-textarea-update")
                    .removeClass("btn-success").addClass("btn-primary")
                    .text("Update player list");
            }, 2000);
        },
        error: function (error) {
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});
