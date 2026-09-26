/**
 * ==========================================================
 * Attachment Manager v2.0
 * ==========================================================
 * Reusable Component for CIMS
 *
 * Features
 * ----------------------------------------------------------
 * ✓ Multiple File Selection
 * ✓ Add Files Multiple Times
 * ✓ Remove File
 * ✓ Prevent Duplicate
 * ✓ Empty State
 * ✓ File Counter
 * ✓ DataTransfer Synchronization
 * ✓ Ready for Drag & Drop
 * ✓ Ready for Image Preview
 * ==========================================================
 */

(function () {

    class AttachmentManager {

        constructor(
            inputId,
            listId,
            counterId = null
        ) {

            this.input = document.getElementById(inputId);

            this.list = document.getElementById(listId);

            this.counter = counterId
                ? document.getElementById(counterId)
                : null;

            // ======================================
            // Source of Truth
            // ======================================

            this.files = [];

            this.initialize();

        }

        // ======================================
        // Initialize
        // ======================================

        initialize() {

            if (!this.input) {

                return;

            }

            this.input.addEventListener(

                "change",

                (event) => {

                    console.log("CHANGE EVENT");

                    console.log(event.target.files);

                    this.addFiles(
                        event.target.files
                    );

                    

                }

            );

            this.render();

        }
        // ======================================
        // Add Files
        // ======================================

        addFiles(fileList) {

            console.log("ADD FILE");

            console.log(fileList);

            Array.from(fileList).forEach(file => {

                console.log(file.name);

                if (!this.exists(file)) {

                    this.files.push(file);

                }

            });

            console.log(this.files);

            this.refresh();

        }

        // ======================================
        // Check Duplicate
        // ======================================

        exists(file) {

            return this.files.some(item =>

                item.name === file.name

                &&

                item.size === file.size

            );

        }

        // ======================================
        // Remove File
        // ======================================

        remove(index) {

            this.files.splice(index, 1);

            this.refresh();

        }

        // ======================================
        // Refresh
        // ======================================

        refresh() {

            console.log("REFRESH");

            console.log(this.files);

            const dt = new DataTransfer();

            this.files.forEach(file => {

                dt.items.add(file);

            });

            this.input.files = dt.files;

            this.render();
            this.isRefreshing = false;

        }

        // ======================================
        // Render
        // ======================================

        render() {

            if (!this.list) {

                return;

            }

            this.list.innerHTML = "";

            if (this.counter) {

                this.counter.textContent = this.files.length;

            }

            // Empty State

            if (this.files.length === 0) {

                this.list.innerHTML =

                    `
                    <div class="attachment-empty">

                        <i class="fas fa-paperclip"></i>

                        <div>

                            No attachment selected

                        </div>

                    </div>
                    `;

                return;

            }

            this.files.forEach(

                (file, index) => {

                    const row =
                        document.createElement("div");

                    row.className =
                        "attachment-item";

                    row.innerHTML =

                        `
                        <div class="attachment-info">

                            ${this.getIcon(file)}

                            <span class="attachment-name">

                                ${file.name}

                            </span>

                            <span class="attachment-size">

                                ${this.formatSize(file.size)}

                            </span>

                        </div>

                        <button
                            type="button"
                            class="btn btn-danger btn-sm attachment-remove">

                            <i class="fas fa-times"></i>

                        </button>
                        `;

                    row.querySelector("button")

                        .addEventListener(

                            "click",

                            () => {

                                this.remove(index);

                            }

                        );

                    this.list.appendChild(row);

                }

            );

        }

        // ======================================
        // File Icon
        // ======================================

        getIcon(file) {

            const ext =
                file.name
                    .split(".")
                    .pop()
                    .toLowerCase();

            switch (ext) {

                case "jpg":
                case "jpeg":
                case "png":
                case "gif":
                case "bmp":
                case "webp":

                    return `
                        <i class="fas fa-image text-success mr-2"></i>
                    `;

                case "pdf":

                    return `
                        <i class="fas fa-file-pdf text-danger mr-2"></i>
                    `;

                case "xls":
                case "xlsx":

                    return `
                        <i class="fas fa-file-excel text-success mr-2"></i>
                    `;

                case "doc":
                case "docx":

                    return `
                        <i class="fas fa-file-word text-primary mr-2"></i>
                    `;

                case "ppt":
                case "pptx":

                    return `
                        <i class="fas fa-file-powerpoint text-warning mr-2"></i>
                    `;

                case "zip":
                case "rar":

                    return `
                        <i class="fas fa-file-archive text-secondary mr-2"></i>
                    `;

                default:

                    return `
                        <i class="fas fa-paperclip text-secondary mr-2"></i>
                    `;

            }

        }

        // ======================================
        // Format File Size
        // ======================================

        formatSize(bytes) {

            if (bytes < 1024) {

                return bytes + " B";

            }

            if (bytes < 1024 * 1024) {

                return (
                    bytes / 1024
                ).toFixed(1) + " KB";

            }

            return (
                bytes / 1024 / 1024
            ).toFixed(2) + " MB";

        }

    }

    // ======================================
    // Auto Initialize
    // ======================================

    document.addEventListener(

        "DOMContentLoaded",

        function () {

            const input =
                document.getElementById(
                    "attachments"
                );

            if (!input) {

                return;

            }

            new AttachmentManager(

                "attachments",

                "attachment-list",

                "attachment-count"

            );

        }

    );

})();