// Globals
var tournament = null
let base_url = "../../"
var nav_index = 0

function render_header() {
    // render name
    $("#tournament_name").html(tournament.name)

    // render status
    if (tournament.status == 0) {
        // new
        $("#tournament_status").html("<span class = 'badge badge-light'>Open for registration</span>")
    } else if (tournament.status == 1) {
        // started
        $("#tournament_status").html("<span class = 'badge badge-success'>Running</span>")
    } else {
        // finished
        $("#tournament_status").html("<span class = 'badge badge-primary'>Closed</span>")
    }
}

function render_main() {
    // switch
    if (tournament.status == 0) {
        render_main_registration()
    } else if (tournament.status == 1) {
        render_main_ongoing(true)
    } else {
        render_main_ongoing(false)
    }
}

function feather_icon(name) {
    return $("<i>").attr("data-feather", name)
}

function render_player_list(table_id, is_render_delete_btn) {
    if (tournament.players.length > 0) {
        tournament.players.map(function(e) {
            $(table_id).find("tbody")
                .append(
                    $('<tr>')
                    .append(
                        $('<td>').append(
                            $('<span>')
                            .attr('class', 'text')
                            .text(e.id)
                        )
                    )
                    .append(
                        $('<td>').append(
                            $('<span>')
                            .attr('class', 'text')
                            .text(e.name)
                        )
                    )
                    .append(
                        $('<td>').append(
                            $('<button>')
                            .attr("class", "btn btn-outline btn-sm")
                            .attr("title", "Delete")
                            .append(
                                feather_icon("delete")
                            )
                            .click(function() {
                                $.ajax({
                                    url: base_url + "api/v1/tournaments/" + tournament.id + "/add/",
                                    method: "DELETE",
                                    contentType: 'application/json',
                                    data: JSON.stringify({
                                        "player": {
                                            "name": e.name
                                        }
                                    }),
                                    success: function(result) {
                                        update()
                                    },
                                    error: function(error) {
                                        console.log(error.status + " " + error.statusText)
                                        console.log(error)
                                    }
                                })
                            })
                        )
                    )
                )
        })
    } else {
        $(table_id).find("tbody")
            .append(
                $('<tr>').append(
                    $('<td>')
                    .attr("rowspan", "2")
                    .append(
                        $('<span>')
                        .text("No players yet")
                    )
                )
            )
    }
}

function render_main_registration() {
    // clear
    $("#main_ongoing").css("display", "none")
    $("#main_registration").css("display", "block")
    $("#tournament-list-table").find("tbody").empty()
    $("#input-playername").val("")

    // render
    $("#next-phase-button")
        .attr("class", "btn btn-sm btn-outline btn-outline-success")
        .html("Begin pairings")

    // render table with players
    render_player_list("#tournament-list-table")

    // render icons
    feather.replace()

    // refocus
    $("#input-playername").focus()
}

function html_score(score, pod_id) {
    if (pod_id === undefined) {
        return "<span>" + score + "</span>"
    }
    return "<span>" + score + " at pod " + pod_id + "</span>"
}


function render_main_ongoing(is_running) {
    // clear
    $("#main_registration").css("display", "none")
    $("#main_ongoing").css("display", "block")
    $("#main_ongoing_body").empty()
    $("#ongoing_nav_list").empty()

    // render next phase button
    $("#next-phase-button")
        .attr("class", "btn btn-sm btn-outline btn-outline-primary")
        .html("Close the tournament")

    // render tabs
    $("#ongoing_nav_list").append(
        $("<li>")
        .attr("class", nav_index == 0 ? "page-item active" : "page-item")
        .append(
            $("<a>")
            .attr("class", "page-link")
            .html("Standings")
            .click(function() {
                nav_index = 0
                update()
            })
        )
    )
    for (var i = 0; i < tournament.rounds.n_rounds; i++) {
        var round_id = i + 1
        $("#ongoing_nav_list").append(
            $("<li>")
            .attr("class", nav_index == i + 1 ? "page-item active" : "page-item")
            .append(
                $("<a>")
                .attr("class", "page-link")
                .attr("data-page-index", round_id)
                .html("Round " + round_id)
                .click(function() {
                    nav_index = $(this).attr("data-page-index")
                    update()
                })
            )
        )
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
        )
        var header_row = $("<tr>")
            .append(
                $("<th>")
                .attr("scope", "col")
                .html("Player")
            )
            .append(
                $("<th>")
                .attr("scope", "col")
                .html("Actions")
            )
            .append(
                $("<th>")
                .attr("scope", "col")
                .html("Total score")
            )
        for (var i = 0; i < tournament.rounds.n_rounds; i++) {
            var round_id = i + 1
            header_row.append(
                $("<th>")
                .attr("scope", "col")
                .html("Round " + round_id)
            )
        }
        $("#table-player-list").find("thead").append(header_row)
        tournament.standings.map(function(e) {
            var row = $("<tr>").append(
                    $('<td>').append(
                        $('<span>')
                        .attr('class', 'text')
                        .text(e.player_name)
                    )
                )
                .append(
                    $('<td>').append(
                        $('<button>')
                        .attr("class", "btn btn-outline btn-sm")
                        .attr("title", "Drop")
                        .append(
                            feather_icon("delete")
                        )
                    )
                )
                .append(
                    $('<td>').append(
                        $('<span>')
                        .attr('class', 'text')
                        .html(html_score(e.total_score))
                    )
                )
            e.rounds.map(function(rnd) {
                row.append(
                    $('<td>')
                    .append(
                        $('<span>')
                        .attr('class', 'text')
                        .html(html_score(rnd.score, rnd.pod_id))
                    )
                )
            })
            $("#table-player-list").find("tbody").append(row)
        })
    } else {
        // render pods
        tournament.rounds.rounds[nav_index - 1].pods.map(function(pod) {
            var rows = $("<div>")
                .attr("class", "rows")
                .append(
                    $("<div>")
                    .attr("class", "row")
                    .append(
                        $("<div>")
                        .attr("class", "col-sm-2")
                        .append(feather_icon("hash"))
                    )
                    .append(
                        $("<div>")
                        .attr("class", "col-sm-6")
                        .text("Player")
                    )
                    .append(
                        $("<div>")
                        .attr("class", "col-sm-2")
                        .text("Score")
                    )
                    .append(
                        $("<div>")
                        .attr("class", "col-sm-2")
                        .text("TB")
                    )
                )
            for (var i = 0; i < pod.players.length; i++) {
                var player_name = pod.players[i]
                var player_score = pod.scores[i]
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
                            .attr("class", "form-control form-control-sm")
                            .attr("data-player-name", player_name)
                            .attr("data-player-score-0", player_score[0])
                            .attr("data-player-score-1", player_score[1])
                            .val(player_score[0] != null ? player_score[0] : null)
                            .change(function() {
                                var e_new_value = $(this).val()
                                var e_player_name = $(this).attr("data-player-name")
                                var old_player_score_1 = $(this).attr("data-player-score-1")
                                $.ajax({
                                    url: base_url + "api/v1/tournaments/" + tournament.id + "/submit/",
                                    method: "POST",
                                    contentType: 'application/json',
                                    data: JSON.stringify({
                                        "player": {
                                            "name": e_player_name
                                        },
                                        "tournament": tournament.id,
                                        "round_id": nav_index - 1,
                                        "score": [e_new_value, old_player_score_1]
                                    }),
                                    success: function(result) {
                                        update()
                                    },
                                    error: function(error) {
                                        console.log(error.status + " " + error.statusText)
                                        console.log(error)
                                    }
                                })
                            })
                        )
                    )
                    .append(
                        $("<div>")
                        .attr("class", "col-sm-2")
                        .append(
                            $("<input>")
                            .attr("type", "number")
                            .attr("class", "form-control form-control-sm")
                            .attr("data-player-name", player_name)
                            .attr("data-player-score-0", player_score[0])
                            .attr("data-player-score-1", player_score[1])
                            .val(player_score[1] != null ? player_score[1] : null)
                            .change(function() {
                                var e_new_value = $(this).val()
                                var e_player_name = $(this).attr("data-player-name")
                                var old_player_score_0 = $(this).attr("data-player-score-0")
                                $.ajax({
                                    url: base_url + "api/v1/tournaments/" + tournament.id + "/submit/",
                                    method: "POST",
                                    contentType: 'application/json',
                                    data: JSON.stringify({
                                        "player": {
                                            "name": e_player_name
                                        },
                                        "tournament": tournament.id,
                                        "round_id": nav_index - 1,
                                        "score": [old_player_score_0, e_new_value]
                                    }),
                                    success: function(result) {
                                        update()
                                    },
                                    error: function(error) {
                                        console.log(error.status + " " + error.statusText)
                                        console.log(error)
                                    }
                                })
                            })
                        )
                    )
                )
            }
            $("#main_ongoing_body").append(rows)
        })
    }

    feather.replace()
}

function render() {
    render_header()
    render_main()
}

function update() {
    $.get({
        url: base_url + "api/v1/tournaments/" + tournament_id + "/",
        success: function(result) {
            tournament = result
            render();
        },
        error: function(error) {
            console.log(error.status + " " + error.statusText)
            console.log(error)
        }
    })
}

$(document).ready(function() {
    update()
})

$("#button-add").click(function() {
    $.post({
        url: base_url + "api/v1/tournaments/" + tournament.id + "/add/",
        contentType: 'application/json',
        data: JSON.stringify({
            "player": {
                "name": $("#input-playername").val()
            }
        }),
        success: function(result) {
            update()
        },
        error: function(error) {
            console.log(error.status + " " + error.statusText)
            console.log(error)
        }
    })
})

$("#next-phase-button").click(function() {
    if (tournament.status < 2) {
        $.ajax({
            url: base_url + "api/v1/tournaments/" + tournament.id + "/",
            method: "PUT",
            contentType: 'application/json',
            data: JSON.stringify({
                "status": tournament.status + 1,
            }),
            success: function(result) {
                update()
            },
            error: function(error) {
                console.log(error.status + " " + error.statusText)
                console.log(error)
            }
        })
    }
})

$("#button-new-round").click(function() {
    $.post({
        url: base_url + "api/v1/tournaments/" + tournament.id + "/round/",
        success: function(result) {
            nav_index = tournament.rounds.n_rounds + 1
            update()
        },
        error: function(error) {
            console.log(error.status + " " + error.statusText)
            console.log(error)
        }
    })
})