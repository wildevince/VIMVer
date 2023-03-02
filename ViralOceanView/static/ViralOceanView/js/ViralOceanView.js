$(document).ready(function () {

    $(".infoPanel").hide();
    $("#infobox-help").click(function () {
        // $("#infoPanel-project").hide(500);
        $("#infoPanel-contact").hide(500);
        $("#infoPanel-help").toggle(1000);
    });
    // $("#infobox-project").click(function() {
    // $("#infoPanel-project").toggle(1000);
    // $("#infoPanel-contact").hide(500);
    // $("#infoPanel-help").hide(500);
    // });
    $("#infobox-contact").click(function () {
        // $("#infoPanel-project").hide(500);
        $("#infoPanel-contact").toggle(1000);
        $("#infoPanel-help").hide(500);
    });
    
});