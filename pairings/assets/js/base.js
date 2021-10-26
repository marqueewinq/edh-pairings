$("#button-login").click(function() {
    let username = $("#input-username").val()
    let password = $("#input-password").val()
    $.post({
        url: base_url + "accounts/login/",
        contentType: 'application/json',
        data: JSON.stringify({
            "username": username,
            "password": password,
        }),
        success: function(result) {
            location.reload()
        },
        error: function(error) {
            console.log(error)
        }
    })
})

$("#button-logout").click(function() {
    $.ajax({
        method: "POST",
        url: base_url + "accounts/logout/",
        headers: get_request_headers(),
        success: function(result) {
            location.reload()
        },
        error: function(error) {
            console.log(error)
        }
    })
})

function get_request_headers() {
    if (auth_token != null && auth_token.length > 0) {
        return {
            "Authorization": "Token " + auth_token
        }
    }
    return {}
}
