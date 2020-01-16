$(document).ready(function() {
    $.get({
        url: "api/v1/tournaments/",
        success: function(result) {
            console.log(result);
        },
        error: function(error) {
            console.log(error)
        }
    })
})