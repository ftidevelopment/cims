document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // Reject Modal
    // ==========================================

    const rejectModal = document.getElementById(
        "rejectModal"
    );

    const rejectModalForm = document.getElementById(
        "rejectModalForm"
    );

    const rejectionReason = document.getElementById(
        "rejection_reason"
    );


    // ==========================================
    // Check Element
    // ==========================================

    if (!rejectModal || !rejectModalForm) {

        return;

    }


    // ==========================================
    // Reject Button
    // ==========================================

    const rejectButtons = document.querySelectorAll(
        ".btn-reject"
    );


    rejectButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                const rejectUrl =
                    button.getAttribute(
                        "data-url"
                    );


                if (!rejectUrl) {

                    console.error(
                        "Reject URL is missing."
                    );

                    return;

                }


                // Set Form Action

                rejectModalForm.setAttribute(
                    "action",
                    rejectUrl
                );


                // Clear Previous Reason

                if (rejectionReason) {

                    rejectionReason.value = "";

                }


                // Open Modal

                $("#rejectModal").modal(
                    "show"
                );

            }
        );

    });


    // ==========================================
    // Reset Form When Modal Closed
    // ==========================================

    $("#rejectModal").on(
        "hidden.bs.modal",
        function () {

            if (rejectionReason) {

                rejectionReason.value = "";

            }

            rejectModalForm.removeAttribute(
                "action"
            );

        }
    );

});