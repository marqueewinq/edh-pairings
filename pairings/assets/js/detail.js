// Globals
var tournament = null
let base_url = "../../"

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

function render_main_registration() {
    // clear
    $("#main_ongoing").css("visibility", "hidden")
    $("#main_registration").css("visibility", "visible")
    $("#tournament-list-table").find("tbody").html("")

    // render
    if (tournament.players.length > 0) {
        tournament.players.map(function(e) {
            $("#tournament-list-table").find("tbody")
                .append(
                    $('<tr>').append(
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
                )
        })
    } else {
        $("#tournament-list-table").find("tbody")
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


function render_main_ongoing(is_running) {

}

function render() {
    render_header()
    render_main()
}

function update() {
    $.get({
        url: base_url + "api/v1/tournaments/" + tournament_id + "/",
        success: function(result) {
            console.log(result);
            tournament = result
            render();
        },
        error: function(error) {
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
            console.log(error)
        }
    })
})