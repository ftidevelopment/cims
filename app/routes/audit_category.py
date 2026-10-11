from io import BytesIO

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import login_required

from app.services.audit_category_service import AuditCategoryService


audit_category_bp = Blueprint(
    "audit_category",
    __name__,
    url_prefix="/audit_categories",
)

service = AuditCategoryService()


# ============================================================
# LIST
# ============================================================

@audit_category_bp.route("/")
@login_required
def index():

    keyword = request.args.get(
        "keyword",
        "",
        type=str,
    )

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    sort_by = request.args.get(
        "sort",
        "created_at",
        type=str,
    )

    sort_order = request.args.get(
        "order",
        "desc",
        type=str,
    )

    is_active = request.args.get(
        "is_active",
        "true",
        type=str,
    )

    if is_active == "true":
        active_filter = True

    elif is_active == "false":
        active_filter = False

    else:
        active_filter = None

    pagination = service.get_all(
        keyword=keyword,
        is_active=active_filter,
        page=page,
        per_page=10,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "audit_category/list.html",

        # IMPORTANT:
        # list.html menggunakan audit_categories
        audit_categories=pagination,

        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active,
    )


# ============================================================
# CREATE
# ============================================================

@audit_category_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
def create():

    if request.method == "POST":

        audit_category_code = request.form.get(
            "audit_category_code",
            "",
        ).strip()

        audit_category_name = request.form.get(
            "audit_category_name",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        try:

            service.create(
                audit_category_code=audit_category_code,
                audit_category_name=audit_category_name,
                description=description or None,
            )

            flash(
                "Audit Category created successfully.",
                "success",
            )

            return redirect(
                url_for("audit_category.index")
            )

        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )

        except Exception as ex:

            flash(
                f"Failed to create Audit Category: {ex}",
                "danger",
            )

    return render_template(
        "audit_category/form.html",
        audit_category=None,
    )


# ============================================================
# EDIT
# ============================================================

@audit_category_bp.route(
    "/edit/<int:audit_category_id>",
    methods=["GET", "POST"],
)
@login_required
def edit(audit_category_id):

    audit_category = service.get_by_id(
        audit_category_id
    )

    if not audit_category:

        flash(
            "Audit Category not found.",
            "danger",
        )

        return redirect(
            url_for("audit_category.index")
        )

    if request.method == "POST":

        audit_category_name = request.form.get(
            "audit_category_name",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        try:

            service.update(
                audit_category=audit_category,
                audit_category_name=audit_category_name,
                description=description or None,
            )

            flash(
                "Audit Category updated successfully.",
                "success",
            )

            return redirect(
                url_for("audit_category.index")
            )

        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )

        except Exception as ex:

            flash(
                f"Failed to update Audit Category: {ex}",
                "danger",
            )

    return render_template(
        "audit_category/form.html",
        audit_category=audit_category,
    )


# ============================================================
# DELETE
# ============================================================

@audit_category_bp.route(
    "/delete/<int:audit_category_id>",
    methods=["POST"],
)
@login_required
def delete(audit_category_id):

    audit_category = service.get_by_id(
        audit_category_id
    )

    if not audit_category:

        flash(
            "Audit Category not found.",
            "danger",
        )

        return redirect(
            url_for("audit_category.index")
        )

    try:

        service.delete(audit_category)

        flash(
            "Audit Category deleted successfully.",
            "success",
        )

    except Exception as ex:

        flash(
            f"Failed to delete Audit Category: {ex}",
            "danger",
        )

    return redirect(
        url_for("audit_category.index")
    )


# ============================================================
# EXPORT EXCEL
# ============================================================

@audit_category_bp.route(
    "/export",
    methods=["GET"],
)
@login_required
def export():

    keyword = request.args.get(
        "keyword",
        "",
        type=str,
    )

    sort_by = request.args.get(
        "sort",
        "created_at",
        type=str,
    )

    sort_order = request.args.get(
        "order",
        "desc",
        type=str,
    )

    is_active = request.args.get(
        "is_active",
        "true",
        type=str,
    )

    if is_active == "true":
        active_filter = True

    elif is_active == "false":
        active_filter = False

    else:
        active_filter = None

    try:

        output = service.export_excel(
            keyword=keyword,
            is_active=active_filter,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        if isinstance(output, BytesIO):

            output.seek(0)

            return send_file(
                output,
                as_attachment=True,
                download_name="audit_categories.xlsx",
                mimetype=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )

        return output

    except Exception as ex:

        flash(
            f"Failed to export Audit Category: {ex}",
            "danger",
        )

        return redirect(
            url_for("audit_category.index")
        )


# ============================================================
# RESTORE
# ============================================================

@audit_category_bp.route(
    "/restore/<int:audit_category_id>",
    methods=["POST"],
)
@login_required
def restore(audit_category_id):

    try:

        result = service.restore(
            audit_category_id
        )

        if result.success:

            flash(
                result.message,
                "success",
            )

        else:

            flash(
                result.message,
                "danger",
            )

    except Exception as ex:

        flash(
            f"Failed to restore Audit Category: {ex}",
            "danger",
        )

    return redirect(
        url_for("audit_category.index")
    )