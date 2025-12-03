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

$(document).on("click", ".delete-tournament", function () {
    const tournamentId = $(this).data("tournament-id");
    const tournamentName = $(this).data("tournament-name");

    if (confirm("Are you sure you want to delete tournament '" + tournamentName + "'? This action cannot be undone.")) {
        $.ajax({
            url: "api/v1/tournaments/" + tournamentId + "/",
            type: "DELETE",
            headers: {
                Authorization: "Token " + auth_token,
            },
            success: function () {
                window.location.reload();
            },
            error: function (error) {
                console.log(error);
                showAPIAlert(error.responseText);
            },
        });
    }
});

feather.replace({
    height: 16,
    width: 16,
});
