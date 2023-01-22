function update_judge_version_description() {
    let judge_version = $("#settings-modal-input-judge-version")
        .find(":selected")
        .val();
    $("#settings-modal-input-judge-version-description-label").html(
        {
            deterministic:
                "<i data-feather='target'></i> Players are distributed according to the standings \
                (from top to bottom; players with buys will have priority). <br> \
                Then, in descending order of standings: if \
                the composition of the players of any of the resulting pods is fully \
                equal to the composition of the pod from some previous round, then the \
                player with the lowest standings of this table changes places at the \
                table with the player with the largest standings from the next table.",
            soft_random:
                "<i data-feather='repeat'></i> Starting from the top player (players with buys will have priority), \
                each other player is assigned a probability to be in the same pod as the \
                current player; then three players are selected according to those \
                probabilities.",
            pure_random:
                "<i data-feather='shuffle'></i> Each round each pod is completely random; although players \
                which already had a buy will not be assigned buy again if possible.",
        }[judge_version]
    );
    feather.replace({
        height: 16,
        width: 16,
    });
}

function render_setting_modal() {
    $("#settings-modal-input-judge-version")
        .change(push_tournament_settings)
        .val(tournament.settings.judge_config.judge_version);
    $("#settings-modal-input-judge-buy-primary")
        .change(push_tournament_settings)
        .val(tournament.settings.judge_config.buy_primary_score);
    $("#settings-modal-input-judge-buy-secondary")
        .change(push_tournament_settings)
        .val(tournament.settings.judge_config.buy_secondary_score);
    $("#settings-modal-input-shuffleseats")
        .change(push_tournament_settings)
        .val(tournament.settings.judge_config.shuffleseats);
    update_judge_version_description();
}

function push_tournament_settings() {
    $.post({
        url: base_url + "api/v1/tournaments/" + tournament.id + "/",
        headers: {
            Authorization: "Token " + auth_token,
        },
        method: "PUT",
        contentType: "application/json",
        data: JSON.stringify({
            settings: {
                judge_config: {
                    judge_version: $("#settings-modal-input-judge-version")
                        .find(":selected")
                        .val(),
                    buy_primary_score: $(
                        "#settings-modal-input-judge-buy-primary"
                    ).val(),
                    buy_secondary_score: $(
                        "#settings-modal-input-judge-buy-secondary"
                    ).val(),
                    shuffle_seats: $("#settings-modal-input-shuffleseats").is(
                        ":checked"
                    ),
                },
            },
        }),
        success: function (result) {
            $("#settings-modal-save-status")
                .empty()
                .append(
                    $("<span>")
                        .attr("class", "text text-muted")
                        .html("All changes saved.")
                        .delay(1000)
                        .fadeOut("slow")
                );
            update_tournament_detail();
        },
        error: function (error) {
            console.log(error.status + " " + error.statusText);
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
}

$("#settings-modal").on("shown.bs.modal", render_setting_modal);
$("#settings-modal-input-judge-version").change(
    update_judge_version_description
);
$("#settings-modal").on("close.bs.modal", update_tournament_detail);
