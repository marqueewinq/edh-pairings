$("#button-login").click(function () {
    let username = $("#input-username").val();
    let password = $("#input-password").val();
    $.post({
        url: base_url + "accounts/login/",
        contentType: "application/json",
        data: JSON.stringify({
            username: username,
            password: password,
        }),
        success: function (result) {
            location.reload();
        },
        error: function (error) {
            console.log(error);
            $("#alert-box-login")
                .empty()
                .append(
                    $("<div>")
                        .attr(
                            "class",
                            "alert alert-warning alert-dismissible fade show"
                        )
                        .attr("role", "alert")
                        .html(
                            "<strong>Holy guacamole!</strong> " +
                                error.responseJSON.detail
                        )
                        .append(
                            $("<button>")
                                .attr("type", "button")
                                .attr("class", "btn-close")
                                .attr("data-bs-dismiss", "alert")
                                .attr("aria-label", "Close")
                        )
                );
        },
    });
});

$("#button-logout").click(function () {
    $.ajax({
        method: "POST",
        url: base_url + "accounts/logout/",
        headers: get_request_headers(),
        success: function (result) {
            location.reload();
        },
        error: function (error) {
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

$("#button-send-login-link").click(function () {
    let email = $("#input-email").val();
    $("#button-send-login-link")
        .removeClass("btn-outline-primary")
        .addClass("btn-outline-warning")
        .html("Sending...");
    $.ajax({
        method: "POST",
        url: base_url + "api/v1/accounts/send-link/",
        data: JSON.stringify({
            email: email,
        }),
        headers: { "Content-type": "application/json" },
        success: function (result) {
            $("#button-send-login-link")
                .removeClass("btn-outline-warning")
                .addClass("btn-outline-success")
                .html("<i data-feather='check'></i> Link sent!");
            feather.replace({
                height: 16,
                width: 16,
            });
        },
        error: function (error) {
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

function get_request_headers() {
    if (auth_token != null && auth_token.length > 0) {
        return {
            Authorization: "Token " + auth_token,
        };
    }
    return {};
}
