from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)
from flask_login import login_required
from app.core.authorization import permission_required
from app.services.audit_service import AuditService
from app.services.audit_report_pdf_service import AuditReportPDFService

audit_bp = Blueprint(
    "audit",
    __name__,
    url_prefix="/audits",
)

service = AuditService()


# ============================================================
# LIST
# ============================================================

@audit_bp.route("/")
@login_required
@permission_required("AUDIT_VIEW")
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
        "audit/list.html",
        audits=pagination,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active,
    )



# ============================================================
# CREATE
# ============================================================

@audit_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@permission_required("AUDIT_CREATE")
def create():

    # --------------------------------------------------------
    # Load master data
    # --------------------------------------------------------

    audit_types = service.get_audit_types()
    audit_categories = service.get_audit_categories()

    if request.method == "POST":

        title = request.form.get(
            "title",
            "",
        ).strip()

        audit_type_id = request.form.get(
            "audit_type_id",
            type=int,
        )

        audit_category_id = request.form.get(
            "audit_category_id",
            type=int,
        )

        audit_date = request.form.get(
            "audit_date",
            "",
        )

        description = request.form.get(
            "description",
            "",
        ).strip()

        status = request.form.get(
            "status",
            "DRAFT",
        )

        try:

            service.create(
                title=title,
                audit_type_id=audit_type_id,
                audit_category_id=audit_category_id,
                audit_date=audit_date,
                description=description or None,
                status=status,
            )

            flash(
                "Audit created successfully.",
                "success",
            )

            return redirect(
                url_for("audit.index")
            )

        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )

        except Exception as ex:

            flash(
                f"Failed to create Audit: {ex}",
                "danger",
            )

    return render_template(
        "audit/form.html",
        audit=None,
        audit_types=audit_types,
        audit_categories=audit_categories,
    )


# ============================================================
# EDIT
# ============================================================

@audit_bp.route(
    "/edit/<int:audit_id>",
    methods=["GET", "POST"],
)
@login_required
@permission_required("AUDIT_EDIT")
def edit(audit_id):

    audit = service.get_by_id(
        audit_id
    )

    if not audit:

        flash(
            "Audit not found.",
            "danger",
        )

        return redirect(
            url_for("audit.index")
        )

    # --------------------------------------------------------
    # Load master data
    # --------------------------------------------------------

    audit_types = service.get_audit_types()
    audit_categories = service.get_audit_categories()

    if request.method == "POST":

        title = request.form.get(
            "title",
            "",
        ).strip()

        audit_type_id = request.form.get(
            "audit_type_id",
            type=int,
        )

        audit_category_id = request.form.get(
            "audit_category_id",
            type=int,
        )

        audit_date = request.form.get(
            "audit_date",
            "",
        )

        description = request.form.get(
            "description",
            "",
        ).strip()

        status = request.form.get(
            "status",
            "DRAFT",
        )

        try:

            service.update(
                audit=audit,
                title=title,
                audit_type_id=audit_type_id,
                audit_category_id=audit_category_id,
                audit_date=audit_date,
                description=description or None,
                status=status,
            )

            flash(
                "Audit updated successfully.",
                "success",
            )

            return redirect(
                url_for("audit.index")
            )

        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )

        except Exception as ex:

            flash(
                f"Failed to update Audit: {ex}",
                "danger",
            )

    return render_template(
        "audit/form.html",
        audit=audit,
        audit_types=audit_types,
        audit_categories=audit_categories,
    )


# ============================================================
# DELETE
# ============================================================

@audit_bp.route(
    "/delete/<int:audit_id>",
    methods=["POST"],
)
@login_required
@permission_required("AUDIT_DELETE")
def delete(audit_id):

    audit = service.get_by_id(
        audit_id
    )

    if not audit:

        flash(
            "Audit not found.",
            "danger",
        )

        return redirect(
            url_for("audit.index")
        )

    try:

        service.delete(audit)

        flash(
            "Audit deleted successfully.",
            "success",
        )

    except Exception as ex:

        flash(
            f"Failed to delete Audit: {ex}",
            "danger",
        )

    return redirect(
        url_for("audit.index")
    )


# ============================================================
# EXPORT EXCEL
# ============================================================

@audit_bp.route(
    "/export",
    methods=["GET"],
)
@login_required
@permission_required("AUDIT_REPORT")
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

        # ==========================================
        # Convert Workbook to BytesIO
        # ==========================================

        if isinstance(output, BytesIO):

            output.seek(0)

        else:

            excel_file = BytesIO()

            output.save(excel_file)

            excel_file.seek(0)

            output = excel_file

        # ==========================================
        # Download Excel
        # ==========================================

        return send_file(
            output,
            as_attachment=True,
            download_name="audits.xlsx",
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

    except Exception as ex:

        flash(
            f"Failed to export Audit: {ex}",
            "danger",
        )

        return redirect(
            url_for("audit.index")
        )

# ============================================================
# RESTORE
# ============================================================

@audit_bp.route(
    "/restore/<int:audit_id>",
    methods=["POST"],
)
@login_required
@permission_required("AUDIT_EDIT")
def restore(audit_id):

    try:

        result = service.restore(
            audit_id
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
            f"Failed to restore Audit: {ex}",
            "danger",
        )

    return redirect(
        url_for("audit.index")
    )


@audit_bp.route(
    "/<int:audit_id>/pdf",
    methods=["GET"]
)
@login_required
@permission_required("AUDIT_REPORT")
def export_pdf(audit_id):

    try:

        audit = service.get_by_id(audit_id)

        if not audit:

            flash(
                "Audit not found.",
                "danger"
            )

            return redirect(
                url_for("audit.index")
            )

        pdf_file = AuditReportPDFService.generate(
            audit_id
        )

        return send_file(
            pdf_file,
            as_attachment=False,
            download_name=(
                f"Audit_Report_{audit.audit_no}.pdf"
            ),
            mimetype="application/pdf",
        )

    except ValueError as e:

        flash(
            str(e),
            "danger"
        )

        return redirect(
            url_for("audit.index")
        )

    except Exception as e:

        flash(
            f"Failed to generate Audit PDF. {e}",
            "danger"
        )

        return redirect(
            url_for("audit.index")
        )
