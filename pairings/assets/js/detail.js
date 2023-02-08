// Globals
var tournament = null;
var nav_index = 0;
var registration_type = 0; // 0 for single-line registration, 1 for bulk edit

function render_header() {
    // render name
    $("#tournament_name").html(tournament.name);

    // render status
    if (tournament.status == 0) {
        // new
        $("#tournament_status").html(
            "<span class = 'badge text-bg-light'>Open for registration</span>"
        );
    } else if (tournament.status == 1) {
        // started
        $("#tournament_status").html(
            "<span class = 'badge text-bg-success'>Running</span>"
        );
    } else {
        // finished
        $("#tournament_status").html(
            "<span class = 'badge text-bg-primary'>Closed</span>"
        );
    }
}

function render_main() {
    // switch
    if (tournament.status == 0) {
        render_main_registration();
    } else if (tournament.status == 1 && is_authenticated) {
        render_main_ongoing(true);
    } else {
        render_main_ongoing(false);
    }

    feather.replace({
        height: 16,
        width: 16,
    });
}

function feather_icon(name) {
    return $("<i>").attr("height", "16").attr("data-feather", name);
}

function render_player_list(table_id, is_render_delete_btn) {
    if (tournament.players.length > 0) {
        tournament.players.map(function (e, index) {
            $(table_id)
                .find("tbody")
                .append(
                    $("<tr>")
                        .append(
                            $("<td>").append(
                                $("<span>")
                                    .attr("class", "text")
                                    .text(index + 1)
                            )
                        )
                        .append(
                            $("<td>").append(
                                $("<span>").attr("class", "text").text(e.name)
                            )
                        )
                        .append(
                            $("<td>").append(
                                $("<button>")
                                    .attr("class", "btn btn-outline btn-sm")
                                    .attr("title", "Delete")
                                    .append(feather_icon("delete"))
                                    .click(function () {
                                        $.ajax({
                                            url:
                                                base_url +
                                                "api/v1/tournaments/" +
                                                tournament.id +
                                                "/add/",
                                            headers: {
                                                Authorization:
                                                    "Token " + auth_token,
                                            },
                                            method: "DELETE",
                                            contentType: "application/json",
                                            data: JSON.stringify({
                                                player: {
                                                    name: e.name,
                                                },
                                            }),
                                            success: function (result) {
                                                update_tournament_detail();
                                            },
                                            error: function (error) {
                                                console.log(
                                                    error.status +
                                                        " " +
                                                        error.statusText
                                                );
                                                console.log(error);
                                                showAPIAlert(
                                                    error.responseText
                                                );
                                            },
                                        });
                                    })
                            )
                        )
                );
        });
    } else {
        $(table_id)
            .find("tbody")
            .append(
                $("<tr>").append(
                    $("<td>")
                        .attr("rowspan", "2")
                        .append($("<span>").text("No players yet"))
                )
            );
    }
}

function render_main_registration() {
    // clear
    $("#main_ongoing").css("display", "none");
    $("#main_registration").css("display", "block");
    $("#tournament-list-table").find("tbody").empty();
    $("#input-playername").val("");

    // render
    $("#next-phase-button")
        .attr("class", "btn btn-sm btn-outline btn-outline-success")
        .html("Begin pairings");

    // render #button-switch-to-textarea and table with players
    //  according to registration_type
    $("#button-switch-to-textarea").empty();
    if (registration_type == 0) {
        $("#button-switch-to-textarea")
            .append(feather_icon("file-text"))
            .append(
                $("<span>")
                    .attr("class", "text")
                    .text(" Paste player names as text")
                    .click(function () {
                        registration_type = 1;
                        render_main();
                    })
            );
        // render table with players
        $("#tournament-list-textarea-input-group").hide();
        $("#tournament-list-textarea").empty().hide();
        $("#tournament-list-table")
            .empty()
            .append($("<thead>"))
            .append($("<tbody>"))
            .show();
        render_player_list("#tournament-list-table");
        $("#tournament-list-table")
            .find("thead")
            .empty()
            .append(
                $("<tr>")
                    .append(
                        $("<th>")
                            .attr("scope", "col")
                            .append(feather_icon("hash"))
                    )
                    .append($("<th>").attr("scope", "col").text("Player name"))
                    .append($("<th>").attr("scope", "col").html(""))
            );
    } else {
        $("#button-switch-to-textarea")
            .append(feather_icon("terminal"))
            .append(
                $("<span>")
                    .attr("class", "text")
                    .text(" Switch to single-line input")
                    .click(function () {
                        registration_type = 0;
                        render_main();
                    })
            );
        // render textarea with players
        $("#tournament-list-textarea-input-group").show();
        $("#tournament-list-textarea").empty().show();
        $("#tournament-list-table").empty().hide();
        var textarea_value = "";
        tournament.players.map(function (e) {
            textarea_value += e.name + "\n";
        });
        $("#tournament-list-textarea")
            .attr(
                "rows",
                tournament.players.length >= 7 ? tournament.players.length : 7
            )
            .val(textarea_value);
    }
}

function html_score(score, pod_id) {
    let score_html =
        "<span title='Primary points'>" +
        score[0] +
        "<span data-feather='chevrons-up' height=16></span>" +
        "</span>" +
        "<span title='Tiebreaker points'>" +
        score[1] +
        "<span data-feather='chevron-up' title='Tiebreaker points' height=16></span>" +
        "</span>";
    if (pod_id === undefined) {
        // for totals
        return "<span>" + score_html + "</span>";
    }
    if (pod_id == null) {
        // buy
        return "<span data-feather='activity' title='Buy' height=16></span> buy";
    }
    return score_html;
}

function render_main_ongoing(is_running) {
    // clear
    $("#tournament-list-table").empty();
    $("#main_ongoing").css("display", "block");
    $("#main_ongoing_body").empty();
    $("#ongoing_nav_list").empty();
    $("#button-new-round").css("display", "");
    $("#button-redo-pairings").css("display", "");
    $("#input-playername-div").css("display", "");

    // render something invisible
    if (!is_running) {
        $("#input-playername-div").css("display", "none");
        $("#button-new-round").css("display", "none");
        $("#button-redo-pairings").css("display", "none");
    }

    // render next phase button
    if (tournament.status == 0) {
        $("#next-phase-button")
            .attr("class", "btn btn-sm btn-outline btn-outline-success ml-2")
            .html(
                "<span data-feather='check' height=16></span> Close the tournament"
            );
    } else if (tournament.status == 1) {
        $("#next-phase-button")
            .attr("class", "btn btn-sm btn-outline btn-outline-primary ml-2")
            .html(
                "<span data-feather='lock' height=16></span> Close the tournament"
            );
    } else {
        $("#next-phase-button")
            .attr("class", "btn btn-sm btn-outline btn-outline-warning ml-2")
            .html(
                "<span data-feather='unlock' height=16></span> Reopen tournament"
            );
    }

    // render tabs
    $("#ongoing_nav_list").append(
        $("<li>")
            .attr("class", nav_index == 0 ? "page-item active" : "page-item")
            .append(
                $("<a>")
                    .attr("class", "page-link")
                    .html("Standings")
                    .click(function () {
                        nav_index = 0;
                        update_tournament_detail();
                    })
            )
    );
    for (var i = 0; i < tournament.rounds.n_rounds; i++) {
        var round_id = i + 1;
        $("#ongoing_nav_list").append(
            $("<li>")
                .attr(
                    "class",
                    nav_index == i + 1 ? "page-item active" : "page-item"
                )
                .append(
                    $("<a>")
                        .attr("class", "page-link")
                        .attr("data-page-index", round_id)
                        .html("Round " + round_id)
                        .click(function () {
                            nav_index = $(this).attr("data-page-index");
                            update_tournament_detail();
                        })
                )
        );
    }

    // render body container
    if (nav_index == 0) {
        // render standings
        $("#main_ongoing_body").append(
            $("<table>")
                .attr("id", "table-player-list")
                .attr("class", "table table-sm")
                .append($("<thead>"))
                .append($("<tbody>"))
        );
        var header_row = $("<tr>")
            .append($("<th>").attr("scope", "col").html("Player"))
            .append($("<th>").attr("scope", "col").html("Status"))
            .append($("<th>").attr("scope", "col").html("Total score"));
        for (var i = 0; i < tournament.rounds.n_rounds; i++) {
            var round_id = i + 1;
            header_row.append(
                $("<th>")
                    .attr("scope", "col")
                    .html("Round " + round_id)
            );
        }
        if (tournament.standings.length > 0) {
            $("#table-player-list").find("thead").append(header_row);
            tournament.standings.map(function (e) {
                var row = $("<tr>")
                    .append(
                        $("<td>").append(
                            $("<span>")
                                .attr("class", "text")
                                .text(e.player_name)
                        )
                    )
                    .append(
                        $("<td>")
                            .append(
                                (function () {
                                    if (e.dropped) {
                                        return $("<span>")
                                            .attr(
                                                "class",
                                                "badge text-bg-danger"
                                            )
                                            .text("dropped");
                                    } else {
                                        return $("<span>")
                                            .attr(
                                                "class",
                                                "badge text-bg-success"
                                            )
                                            .text("active");
                                    }
                                })()
                            )
                            .append(
                                (function () {
                                    if (e.dropped || !is_running) {
                                        return $("<span>");
                                    }
                                    return $("<button>")
                                        .attr("class", "btn btn-outline btn-sm")
                                        .attr("title", "Drop")
                                        .append(feather_icon("delete"))
                                        .click(function () {
                                            $.ajax({
                                                url:
                                                    base_url +
                                                    "api/v1/tournaments/" +
                                                    tournament.id +
                                                    "/drop/",
                                                headers: {
                                                    Authorization:
                                                        "Token " + auth_token,
                                                },
                                                method: "POST",
                                                contentType: "application/json",
                                                data: JSON.stringify({
                                                    player: {
                                                        name: e.player_name,
                                                    },
                                                }),
                                                success: function (result) {
                                                    update_tournament_detail();
                                                },
                                                error: function (error) {
                                                    console.log(
                                                        error.status +
                                                            " " +
                                                            error.statusText
                                                    );
                                                    console.log(error);
                                                    showAPIAlert(
                                                        error.responseText
                                                    );
                                                },
                                            });
                                        });
                                })()
                            )
                    )
                    .append(
                        $("<td>").append(
                            $("<span>")
                                .attr("class", "text-justify")
                                .html(html_score(e.total_score))
                        )
                    );
                e.rounds.map(function (rnd) {
                    row.append(
                        $("<td>")
                            .append(
                                $("<span>")
                                    .attr("class", "align-center")
                                    .html(html_score(rnd.score, rnd.pod_id))
                            )
                            .attr("class", "align-center")
                    );
                });
                $("#table-player-list").find("tbody").append(row);
            });
        } else {
            render_player_list("#table-player-list");

            // hide Status column
            $("#main_ongoing_body")
                .find("table")
                .find("td:nth-child(3),th:nth-child(3)")
                .hide();
        }
    } else {
        // render round page

        // render copy to clipboard button
        // $("#main_ongoing_body").append(
        //     $("<div>")
        //     .attr("class", "d-flex justify-content-center")
        //     .append(
        //         $("<button>")
        //         .attr("class", "btn btn-outline-primary")
        //         .append(feather_icon("clipboard"))
        //         .append(
        //             $("<span>")
        //             .text("Copy round pairing to clipboard")
        //         )
        //         .click(copy_round_to_clipboard())
        //     )
        // )

        $("#main_ongoing_body").append(
            $("<table>")
                .attr("id", "table-player-list")
                .attr("class", "table table-sm")
                .append($("<thead>"))
                .append($("<tbody>"))
        );

        // render buys
        if (tournament.rounds.rounds[nav_index - 1].buys.length > 0) {
            var buys_list = $("<div>").attr("class", "rows ml-4");

            tournament.rounds.rounds[nav_index - 1].buys.map(function (buy) {
                buys_list.append($("<div>").attr("class", "row").text(buy));
            });

            var buys = $("<div>")
                .attr("class", "rows")
                .append(
                    $("<div>")
                        .attr("class", "row")
                        .append(
                            $("<div>")
                                .attr(
                                    "class",
                                    "col-sm-6 d-flex align-items-center justify-content-center"
                                )
                                .append(feather_icon("activity"))
                                .append($("<strong>").text("Buys"))
                        )
                        .append(
                            $("<div>")
                                .attr("class", "col-sm-6 border-left")
                                .append(buys_list)
                        )
                );

            $("#main_ongoing_body").append(buys);
        }

        // render pods
        pod_id = 0;
        tournament.rounds.rounds[nav_index - 1].pods.map(function (pod) {
            pod_id += 1;
            var rows = $("<div>")
                .attr("class", "rows")
                .append(
                    $("<div>")
                        .attr("class", "row mt-3 mb-1 border-bottom")
                        .append(
                            $("<div>")
                                .attr("class", "col-sm-2")
                                .text("Pod #" + pod_id)
                        )
                        .append(
                            $("<div>").attr("class", "col-sm-6").text("Player")
                        )
                        .append(
                            $("<div>")
                                .attr("class", "col-sm-2")
                                .html(
                                    "Score <span data-feather='chevrons-up' height=16></span>"
                                )
                        )
                        .append(
                            $("<div>")
                                .attr("class", "col-sm-2")
                                .html(
                                    "TB <span data-feather='chevron-up' height=16></span>"
                                )
                        )
                );
            for (var i = 0; i < pod.players.length; i++) {
                var player_name = pod.players[i];
                var player_score = pod.scores[i];
                rows.append(
                    $("<div>")
                        .attr("class", "row")
                        .append(
                            $("<div>")
                                .attr("class", "col-sm-2")
                                .text(i + 1)
                        )
                        .append(
                            $("<div>")
                                .attr("class", "col-sm-6")
                                .text(player_name)
                        )
                        .append(
                            $("<div>")
                                .attr("class", "col-sm-2")
                                .append(
                                    $("<input>")
                                        .attr("type", "number")
                                        .attr(
                                            "class",
                                            "form-control form-control-sm"
                                        )
                                        .attr("data-player-name", player_name)
                                        .attr("readonly", !is_running)
                                        .val(
                                            player_score[0] != null
                                                ? player_score[0]
                                                : null
                                        )
                                        .change(function () {
                                            var e_new_value = $(this).val();
                                            var e_player_name = $(this).attr(
                                                "data-player-name"
                                            );
                                            $.ajax({
                                                url:
                                                    base_url +
                                                    "api/v1/tournaments/" +
                                                    tournament.id +
                                                    "/submit/",
                                                headers: {
                                                    Authorization:
                                                        "Token " + auth_token,
                                                },
                                                method: "POST",
                                                contentType: "application/json",
                                                data: JSON.stringify({
                                                    player: {
                                                        name: e_player_name,
                                                    },
                                                    round_id: nav_index - 1,
                                                    score: [
                                                        parseInt(e_new_value),
                                                        null,
                                                    ],
                                                }),
                                                success: function (result) {
                                                    console.log(
                                                        "Score updated"
                                                    );
                                                },
                                                error: function (error) {
                                                    console.log(
                                                        error.status +
                                                            " " +
                                                            error.statusText
                                                    );
                                                    console.log(error);
                                                    showAPIAlert(
                                                        error.responseText
                                                    );
                                                },
                                            });
                                        })
                                )
                        )
                        .append(
                            $("<div>")
                                .attr("class", "col-sm-2")
                                .append(
                                    $("<input>")
                                        .attr("type", "number")
                                        .attr(
                                            "class",
                                            "form-control form-control-sm"
                                        )
                                        .attr("data-player-name", player_name)
                                        .attr("readonly", !is_running)
                                        .val(
                                            player_score[1] != null
                                                ? player_score[1]
                                                : null
                                        )
                                        .change(function () {
                                            var e_new_value = $(this).val();
                                            var e_player_name = $(this).attr(
                                                "data-player-name"
                                            );
                                            $.ajax({
                                                url:
                                                    base_url +
                                                    "api/v1/tournaments/" +
                                                    tournament.id +
                                                    "/submit/",
                                                headers: {
                                                    Authorization:
                                                        "Token " + auth_token,
                                                },
                                                method: "POST",
                                                contentType: "application/json",
                                                data: JSON.stringify({
                                                    player: {
                                                        name: e_player_name,
                                                    },
                                                    tournament: tournament.id,
                                                    round_id: nav_index - 1,
                                                    score: [
                                                        null,
                                                        parseInt(e_new_value),
                                                    ],
                                                }),
                                                success: function (result) {
                                                    console.log(
                                                        "Score updated"
                                                    );
                                                },
                                                error: function (error) {
                                                    console.log(
                                                        error.status +
                                                            " " +
                                                            error.statusText
                                                    );
                                                    console.log(error);
                                                    showAPIAlert(
                                                        error.responseText
                                                    );
                                                },
                                            });
                                        })
                                )
                        )
                );
            }
            $("#main_ongoing_body").append(rows);
        });
    }
}

function render_tournament_detail() {
    render_header();
    render_main();
}

function update_tournament_detail() {
    $.get({
        url: base_url + "api/v1/tournaments/" + tournament_id + "/",
        headers: get_request_headers(),
        success: function (result) {
            tournament = result;
            render_tournament_detail();
        },
        error: function (error) {
            console.log(error.status + " " + error.statusText);
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
        url: base_url + "api/v1/tournaments/" + tournament.id + "/add/",
        headers: get_request_headers(),
        contentType: "application/json",
        data: JSON.stringify({
            player: {
                name: $("#input-playername").val(),
            },
        }),
        success: function (result) {
            update_tournament_detail();

            // refocus
            $("#input-playername").val("");
            $("#input-playername").focus();
        },
        error: function (error) {
            console.log(error.status + " " + error.statusText);
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

$("#next-phase-button").click(function () {
    if (tournament.status < 2) {
        $.ajax({
            url: base_url + "api/v1/tournaments/" + tournament.id + "/",
            headers: {
                Authorization: "Token " + auth_token,
            },
            method: "PUT",
            contentType: "application/json",
            data: JSON.stringify({
                status: parseInt(tournament.status + 1),
            }),
            success: function (result) {
                update_tournament_detail();
            },
            error: function (error) {
                console.log(error.status + " " + error.statusText);
                console.log(error);
                showAPIAlert(error.responseText);
            },
        });
    } else {
        $.ajax({
            url: base_url + "api/v1/tournaments/" + tournament.id + "/",
            headers: {
                Authorization: "Token " + auth_token,
            },
            method: "PUT",
            contentType: "application/json",
            data: JSON.stringify({
                status: 1,
            }),
            success: function (result) {
                update_tournament_detail();
            },
            error: function (error) {
                console.log(error.status + " " + error.statusText);
                console.log(error);
                showAPIAlert(error.responseText);
            },
        });
    }
});

$("#button-new-round").click(function () {
    $.post({
        url: base_url + "api/v1/tournaments/" + tournament.id + "/round/",
        headers: get_request_headers(),
        success: function (result) {
            nav_index = parseInt(result.rounds.n_rounds);
            update_tournament_detail();
        },
        error: function (error) {
            console.log(error.status + " " + error.statusText);
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

$("#button-redo-pairings").click(function () {
    $.post({
        url: base_url + "api/v1/tournaments/" + tournament.id + "/round/redo/",
        headers: get_request_headers(),
        success: function (result) {
            nav_index = parseInt(tournament.rounds.n_rounds);
            update_tournament_detail();
        },
        error: function (error) {
            console.log(error.status + " " + error.statusText);
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

function parse_textarea_into_player_names() {
    let player_names = $("#tournament-list-textarea").val().split("\n");
    var result = [];
    player_names.map(function (e) {
        if (e.length > 0) {
            result.push({ name: e });
        }
    });
    return result;
}

$("#tournament-list-textarea-update").click(function () {
    $.post({
        url: base_url + "api/v1/tournaments/" + tournament.id + "/bulk-edit/",
        headers: get_request_headers(),
        contentType: "application/json",
        data: JSON.stringify({ players: parse_textarea_into_player_names() }),
        success: function (result) {
            update_tournament_detail();
            $("#tournament-list-textarea").focus();
            $("#tournament-list-textarea-update")
                .removeClass("btn-outline-secondary")
                .addClass("btn-outline-success")
                .empty()
                .append(feather_icon("check"))
                .append($("<span>").text(" Player list updated"));
            setTimeout(function () {
                $("#tournament-list-textarea-update")
                    .removeClass("btn-outline-success")
                    .addClass("btn-outline-secondary")
                    .text("Update");
            }, 2000);
        },
        error: function (error) {
            console.log(error.status + " " + error.statusText);
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});
