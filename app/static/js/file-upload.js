(function () {

    function initializeFileUpload() {

        const fileInputs = document.querySelectorAll(
            ".custom-file-input"
        );

        fileInputs.forEach(function (input) {

            input.addEventListener(
                "change",
                function () {

                    updateFileLabel(this);

                }
            );

        });

    }

    function updateFileLabel(input) {

        const label = input.nextElementSibling;

        if (!label) {
            return;
        }

        if (input.files.length === 0) {

            label.textContent = "Choose file...";

            return;

        }

        // Single File
        if (input.files.length === 1) {

            label.textContent =
                input.files[0].name;

            return;

        }

        // Multiple Files
        const fileNames = [];

        for (
            let i = 0;
            i < input.files.length;
            i++
        ) {

            fileNames.push(
                input.files[i].name
            );

        }

        label.textContent =
            fileNames.join(", ");

    }

    document.addEventListener(
        "DOMContentLoaded",
        initializeFileUpload
    );

})();