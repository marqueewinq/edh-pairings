var frozen_alert = false;

function _show_api_alert(message) {
    $("#alert-api-error")
        .html(
            "<button type='button' class='btn' " +
                "onclick='_freeze_api_alert()'><i data-feather='eye'></i> Freeze</button>" +
            "<button type='button' class='btn' id='send-and-update-button' " +
                "onclick='_send_and_update()'><i data-feather='navigation'></i> Send to developer</button>" +
                "<div>" +
                message +
                "</div>" +
                "<button type='button' class='btn-close' " +
                "onclick='_hide_api_alert()' aria-label='Close'></button>"
        )
        .removeClass("hide")
        .addClass("show");
    feather.replace({
        height: 16,
        width: 16
    })
}

function _send_and_update() {
    // TODO: send to sentry
    $("#send-and-update-button").addClass("btn-outline-success").html("<i data-feather='check'></i> Thank you!")
    feather.replace({
        height: 16,
        width: 16
    })
}

function _freeze_api_alert() {
    frozen_alert = true;
}

function _hide_api_alert_if_not_frozen() {
    if (!frozen_alert) {
        _hide_api_alert();
    }
}

function _hide_api_alert() {
    frozen_alert = false;
    $("#alert-api-error").empty().removeClass("show").addClass("hide");
}
function showAPIAlert(message) {
    _show_api_alert(message);
    setTimeout(_hide_api_alert_if_not_frozen, 5000);
    return false;
}

$("#alert-api-error").on("close.bs.alert", showAPIAlert);
