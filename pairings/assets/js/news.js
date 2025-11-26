let has_read_current_new_tag_cookie_name =
    "edh-pairings-news-modal-read-version";

$("#newsModal").on("hidden.bs.modal", function () {
    Cookies.set(has_read_current_new_tag_cookie_name, latest_news_tag, {
        domain: document.location.hostname,
        SameSite: "Lax",
    });
    set_alert_visibility();
});

$("#news-switch-EN-button").click(function () {
    $("#news-body-en").show()
    $("#news-body-ru").hide()
    $("#news-switch-EN-button").removeClass("btn-secondary").addClass("btn-primary")
    $("#news-switch-RU-button").removeClass("btn-primary").addClass("btn-secondary")

})
$("#news-switch-RU-button").click(function () {
    $("#news-body-en").hide()
    $("#news-body-ru").show()
    $("#news-switch-EN-button").removeClass("btn-primary").addClass("btn-secondary")
    $("#news-switch-RU-button").removeClass("btn-secondary").addClass("btn-primary")
})

function has_read_current_news_tag() {
    if (latest_news_tag.length == 0) {
        return true;
    }
    let cookie = Cookies.get(has_read_current_new_tag_cookie_name);
    return cookie && cookie == latest_news_tag;
}

function set_alert_visibility() {
    if (has_read_current_news_tag()) {
        $("#alert-unread-news").remove();
    } else {
        $("#alert-unread-news").removeClass("hide").addClass("show");
    }
}

set_alert_visibility();
