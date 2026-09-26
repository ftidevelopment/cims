$(document).ready(function () {

    // ==================================================
    // Restore Modal
    // ==================================================

    $(document).on(
        "click",
        ".btn-restore",
        function () {

            const name = $(this).data("name");
            const url = $(this).data("url");

            // ------------------------------------------
            // Set Item Name
            // ------------------------------------------

            $("#restore-item-name").text(
                name
            );

            // ------------------------------------------
            // Set Form Action
            // ------------------------------------------

            $("#restore-form").attr(
                "action",
                url
            );

        }
    );

});