document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll("form");

    forms.forEach(form => {

        form.addEventListener("submit", function (event) {

            // ==================================================
            // Convert Jodit HTML to Plain Text
            // ==================================================

            form.querySelectorAll(
                "textarea[data-jodit-plain-text='true']"
            ).forEach(field => {

                if (field.value) {

                    const tempDiv =
                        document.createElement("div");

                    tempDiv.innerHTML = field.value;

                    // Convert <br> to newline
                    tempDiv
                        .querySelectorAll("br")
                        .forEach(br => {
                            br.replaceWith("\n");
                        });

                    // Convert paragraph/div/list blocks
                    tempDiv
                        .querySelectorAll(
                            "p, div, li"
                        )
                        .forEach(element => {

                            element.insertAdjacentText(
                                "beforebegin",
                                "\n"
                            );

                        });

                    // Get plain text
                    let plainText =
                        tempDiv.innerText ||
                        tempDiv.textContent ||
                        "";

                    // Normalize line breaks
                    plainText =
                        plainText
                            .replace(/\n\s*\n+/g, "\n")
                            .trim();

                    field.value = plainText;

                }

            });


            // ==================================================
            // Required Field Validation
            // ==================================================

            let valid = true;

            form.querySelectorAll(
                "[required]"
            ).forEach(field => {

                const value =
                    field.value.trim();

                const feedback =
                    field.nextElementSibling;

                if (value === "") {

                    valid = false;

                    field.classList.add(
                        "is-invalid"
                    );

                    if (
                        feedback &&
                        feedback.classList.contains(
                            "invalid-feedback"
                        )
                    ) {

                        feedback.textContent =
                            (
                                field.dataset.label ||
                                field.name ||
                                "This field"
                            ) +
                            " is required.";

                    }

                } else {

                    field.classList.remove(
                        "is-invalid"
                    );

                }

            });


            // ==================================================
            // Prevent Submit if Invalid
            // ==================================================

            if (!valid) {

                event.preventDefault();

                const firstInvalid =
                    form.querySelector(
                        ".is-invalid"
                    );

                if (firstInvalid) {

                    firstInvalid.focus();

                }

            }

        });

    });


    // ==================================================
    // Clear Validation on Input
    // ==================================================

    document
        .querySelectorAll("[required]")
        .forEach(field => {

            field.addEventListener(
                "input",
                function () {

                    if (
                        field.value.trim() !== ""
                    ) {

                        field.classList.remove(
                            "is-invalid"
                        );

                    }

                }
            );

        });

});