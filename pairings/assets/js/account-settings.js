function render_user_settings_modal() {
    $.ajax({
        url: base_url + "api/v1/accounts/" + user_id + "/",
        headers: {
            Authorization: "Token " + auth_token,
        },
        method: "GET",
        contentType: "application/json",
        success: function (result) {
            $("#user-settings-modal-input-username")
                .change(push_user_settings)
                .val(result.username);
            $("#user-settings-modal-input-email")
                .change(push_user_settings)
                .val(result.email);
        },
        error: function (error) {
            console.log(error.status + " " + error.statusText);
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
}

function reset_validation() {
    $("#user-settings-modal-input-username").removeClass("is-valid is-invalid");
    $("#user-settings-modal-input-username-feedback")
        .removeClass("invalid-feedback")
        .empty();
    $("#user-settings-modal-input-email").removeClass("is-valid is-invalid");
    $("#user-settings-modal-input-email-feedback")
        .removeClass("invalid-feedback")
        .empty();
}

function push_user_settings() {
    $.post({
        url: base_url + "api/v1/accounts/" + user_id + "/",
        headers: {
            Authorization: "Token " + auth_token,
        },
        method: "PUT",
        contentType: "application/json",
        data: JSON.stringify({
            username: $("#user-settings-modal-input-username").val(),
            email: $("#user-settings-modal-input-email").val(),
        }),
        success: function (result) {
            $("#user-settings-modal-save-status")
                .empty()
                .append(
                    $("<span>")
                        .attr("class", "text text-muted")
                        .html("All changes saved.")
                        .delay(1000)
                        .fadeOut("slow")
                );
            reset_validation();
        },
        error: function (error) {
            reset_validation();
            if (error.status == 400) {
                if (error.responseJSON.username === undefined) {
                    $("#user-settings-modal-input-username").addClass(
                        "is-valid"
                    );
                } else {
                    $("#user-settings-modal-input-username").addClass(
                        "is-invalid"
                    );
                    $("#user-settings-modal-input-username-feedback")
                        .addClass("invalid-feedback")
                        .html(error.responseJSON.username);
                }
                if (error.responseJSON.email === undefined) {
                    $("#user-settings-modal-input-email").addClass("is-valid");
                } else {
                    $("#user-settings-modal-input-email").addClass(
                        "is-invalid"
                    );
                    $("#user-settings-modal-input-email-feedback")
                        .addClass("invalid-feedback")
                        .html(error.responseJSON.email);
                }
            } else {
                console.log(error.status + " " + error.statusText);
                console.log(error);
                showAPIAlert(error.responseText);
            }
        },
    });
}

$("#user-settings-modal").on("shown.bs.modal", render_user_settings_modal);
