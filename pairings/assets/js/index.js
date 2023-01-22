$("#button-new-tournament").click(function () {
    name = $("#input-name").val();
    $.post({
        url: "api/v1/tournaments/",
        headers: {
            Authorization: "Token " + auth_token,
        },
        contentType: "application/json",
        data: JSON.stringify({
            name: name,
        }),
        success: function (result) {
            window.location.href = "/tournaments/" + result.id + "/";
        },
        error: function (error) {
            console.log(error);
            showAPIAlert(error.responseText);
        },
    });
});

feather.replace({
    height: 16,
    width: 16,
});
