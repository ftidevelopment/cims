/**
 * ==========================================================
 * Delete Modal
 * ==========================================================
 * Reusable Component for CIMS
 *
 * Usage:
 *
 * <button
 *      class="btn-delete"
 *      data-name="Department A"
 *      data-url="/department/delete/1">
 * </button>
 *
 * ==========================================================
 */

$(function () {

    $(document).on(

        "click",

        ".btn-delete",

        function () {

            const name = $(this).data("name");

            const url = $(this).data("url");

            $("#delete-item-name").text(name);

            $("#delete-form").attr(
                "action",
                url
            );

            $("#deleteModal").modal(
                "show"
            );

        }

    );

});