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

from app.services.audit_checklist_service import (
    AuditChecklistService,
)
from app.services.audit_checklist_item_service import (
    AuditChecklistItemService,
)


audit_checklist_bp = Blueprint(
    "audit_checklist",
    __name__,
    url_prefix="/audit_checklists",
)

service = AuditChecklistService()
item_service = AuditChecklistItemService()

# ==========================================================
# LIST
# ==========================================================

@audit_checklist_bp.route("/", methods=["GET"])
@login_required
def index():
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

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int,
    )

    pagination = service.get_all(
        keyword=keyword,
        is_active=active_filter,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "audit_checklist/list.html",
        audit_checklists=pagination,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active,
    )


# ==========================================================
# CREATE
# ==========================================================

@audit_checklist_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
def create():

    if request.method == "POST":

        audit_checklist_code = request.form.get(
            "audit_checklist_code",
            "",
        ).strip()

        audit_checklist_name = request.form.get(
            "audit_checklist_name",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        try:

            service.create(
                audit_checklist_code=audit_checklist_code,
                audit_checklist_name=audit_checklist_name,
                description=description or None,
            )

            flash(
                "Audit Checklist created successfully.",
                "success",
            )

            return redirect(
                url_for("audit_checklist.index")
            )

        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )

        except Exception as ex:

            flash(
                f"Failed to create Audit Checklist: {ex}",
                "danger",
            )

    return render_template(
        "audit_checklist/form.html",
        audit_checklist=None,
    )


# ==========================================================
# EDIT
# ==========================================================

@audit_checklist_bp.route(
    "/<int:audit_checklist_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(audit_checklist_id):

    audit_checklist = service.get_by_id(
        audit_checklist_id
    )

    if not audit_checklist:

        flash(
            "Audit Checklist not found.",
            "danger",
        )

        return redirect(
            url_for("audit_checklist.index")
        )

    if request.method == "POST":

        audit_checklist_name = request.form.get(
            "audit_checklist_name",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        try:

            service.update(
                audit_checklist=audit_checklist,
                audit_checklist_name=audit_checklist_name,
                description=description or None,
            )

            flash(
                "Audit Checklist updated successfully.",
                "success",
            )

            return redirect(
                url_for("audit_checklist.index")
            )

        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )

        except Exception as ex:

            flash(
                f"Failed to update Audit Checklist: {ex}",
                "danger",
            )

    return render_template(
        "audit_checklist/form.html",
        audit_checklist=audit_checklist,
    )


# ==========================================================
# DELETE
# ==========================================================

@audit_checklist_bp.route(
    "/<int:audit_checklist_id>/delete",
    methods=["POST"],
)
@login_required
def delete(audit_checklist_id):

    audit_checklist = service.get_by_id(
        audit_checklist_id
    )

    if not audit_checklist:

        flash(
            "Audit Checklist not found.",
            "danger",
        )

        return redirect(
            url_for("audit_checklist.index")
        )

    try:

        service.delete(audit_checklist)

        flash(
            "Audit Checklist deleted successfully.",
            "success",
        )

    except Exception as ex:

        flash(
            f"Failed to delete Audit Checklist: {ex}",
            "danger",
        )

    return redirect(
        url_for("audit_checklist.index")
    )


# ==========================================================
# RESTORE
# ==========================================================

@audit_checklist_bp.route(
    "/<int:audit_checklist_id>/restore",
    methods=["POST"],
)
@login_required
def restore(audit_checklist_id):

    try:

        result = service.restore(
            audit_checklist_id
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
            f"Failed to restore Audit Checklist: {ex}",
            "danger",
        )

    return redirect(
        url_for("audit_checklist.index")
    )


# ==========================================================
# EXPORT EXCEL
# ==========================================================

@audit_checklist_bp.route(
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

        else:

            excel_file = BytesIO()

            output.save(excel_file)

            excel_file.seek(0)

            output = excel_file

        return send_file(
            output,
            as_attachment=True,
            download_name="audit_checklists.xlsx",
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

    except Exception as ex:

        flash(
            f"Failed to export Audit Checklist: {ex}",
            "danger",
        )

        return redirect(
            url_for("audit_checklist.index")
        )

@audit_checklist_bp.route(
    "/<int:audit_checklist_id>",
    methods=["GET"],
)
@login_required
def detail(audit_checklist_id):

    audit_checklist = service.get_by_id(
        audit_checklist_id
    )

    if not audit_checklist:

        flash(
            "Audit Checklist not found.",
            "danger",
        )

        return redirect(
            url_for("audit_checklist.index")
        )

    # ======================================================
    # ITEM STATUS FILTER
    # ======================================================

    item_status = request.args.get(
        "item_status",
        "active",
        type=str,
    )

    if item_status == "active":
        item_active_filter = True

    elif item_status == "inactive":
        item_active_filter = False

    else:
        item_status = "all"
        item_active_filter = None

    # ======================================================
    # GET CHECKLIST ITEMS
    # ======================================================

    items = item_service.get_by_checklist_status(
        audit_checklist_id=audit_checklist_id,
        is_active=item_active_filter,
    )

    return render_template(
        "audit_checklist/detail.html",
        audit_checklist=audit_checklist,
        items=items,
        item_status=item_status,
    )

# ==========================================================
# CREATE CHECKLIST ITEM
# ==========================================================

@audit_checklist_bp.route(
    "/<int:audit_checklist_id>/items/create",
    methods=["GET", "POST"],
)
@login_required
def create_item(audit_checklist_id):

    audit_checklist = service.get_by_id(
        audit_checklist_id
    )

    if not audit_checklist:

        flash(
            "Audit Checklist not found.",
            "danger",
        )

        return redirect(
            url_for("audit_checklist.index")
        )


    if request.method == "POST":

        question = request.form.get(
            "question",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        is_required = (
            request.form.get("is_required") == "1"
        )

        item_no = request.form.get(
            "item_no",
            "",
        ).strip()

        sort_order = request.form.get(
            "sort_order",
            "",
        ).strip()


        # Empty value means automatic numbering
        if item_no == "":
            item_no = None

        if sort_order == "":
            sort_order = None


        try:

            item = item_service.create(
                audit_checklist_id=audit_checklist_id,
                question=question,
                description=description or None,
                is_required=is_required,
                item_no=item_no,
                sort_order=sort_order,
            )

            flash(
                f"Checklist Item {item.item_no} created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "audit_checklist.detail",
                    audit_checklist_id=audit_checklist_id,
                )
            )


        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )


        except Exception as ex:

            flash(
                f"Failed to create Checklist Item: {ex}",
                "danger",
            )


    return render_template(
        "audit_checklist/item_form.html",
        audit_checklist=audit_checklist,
        item=None,
    )


# ==========================================================
# EDIT CHECKLIST ITEM
# ==========================================================

@audit_checklist_bp.route(
    "/<int:audit_checklist_id>/items/<int:item_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_item(
    audit_checklist_id,
    item_id,
):

    audit_checklist = service.get_by_id(
        audit_checklist_id
    )

    if not audit_checklist:

        flash(
            "Audit Checklist not found.",
            "danger",
        )

        return redirect(
            url_for("audit_checklist.index")
        )


    item = item_service.get_by_id(
        item_id
    )

    if not item:

        flash(
            "Audit Checklist Item not found.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_checklist.detail",
                audit_checklist_id=audit_checklist_id,
            )
        )


    # Make sure the item belongs to this checklist
    if item.audit_checklist_id != audit_checklist_id:

        flash(
            "Invalid Audit Checklist Item.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_checklist.detail",
                audit_checklist_id=audit_checklist_id,
            )
        )


    if request.method == "POST":

        question = request.form.get(
            "question",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        is_required = (
            request.form.get("is_required") == "1"
        )

        item_no = request.form.get(
            "item_no",
            "",
        ).strip()

        sort_order = request.form.get(
            "sort_order",
            "",
        ).strip()


        if item_no == "":
            item_no = None

        if sort_order == "":
            sort_order = None


        try:

            item_service.update(
                item=item,
                question=question,
                description=description or None,
                is_required=is_required,
                item_no=item_no,
                sort_order=sort_order,
            )

            flash(
                f"Checklist Item {item.item_no} updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "audit_checklist.detail",
                    audit_checklist_id=audit_checklist_id,
                )
            )


        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )


        except Exception as ex:

            flash(
                f"Failed to update Checklist Item: {ex}",
                "danger",
            )


    return render_template(
        "audit_checklist/item_form.html",
        audit_checklist=audit_checklist,
        item=item,
    )

# ==========================================================
# DELETE CHECKLIST ITEM
# ==========================================================

@audit_checklist_bp.route(
    "/<int:audit_checklist_id>/items/<int:item_id>/delete",
    methods=["POST"],
)
@login_required
def delete_item(
    audit_checklist_id,
    item_id,
):

    audit_checklist = service.get_by_id(
        audit_checklist_id
    )

    if not audit_checklist:

        flash(
            "Audit Checklist not found.",
            "danger",
        )

        return redirect(
            url_for("audit_checklist.index")
        )


    item = item_service.get_by_id(
        item_id
    )

    if not item:

        flash(
            "Audit Checklist Item not found.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_checklist.detail",
                audit_checklist_id=audit_checklist_id,
            )
        )


    if item.audit_checklist_id != audit_checklist_id:

        flash(
            "Invalid Audit Checklist Item.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_checklist.detail",
                audit_checklist_id=audit_checklist_id,
            )
        )


    try:

        item_no = item.item_no

        item_service.delete(
            item
        )

        flash(
            f"Checklist Item {item_no} deleted successfully.",
            "success",
        )

    except Exception as ex:

        flash(
            f"Failed to delete Checklist Item: {ex}",
            "danger",
        )


    return redirect(
        url_for(
            "audit_checklist.detail",
            audit_checklist_id=audit_checklist_id,
        )
    )

# ==========================================================
# RESTORE CHECKLIST ITEM
# ==========================================================

@audit_checklist_bp.route(
    "/<int:audit_checklist_id>/items/<int:item_id>/restore",
    methods=["POST"],
)
@login_required
def restore_item(
    audit_checklist_id,
    item_id,
):

    audit_checklist = service.get_by_id(
        audit_checklist_id
    )

    if not audit_checklist:

        flash(
            "Audit Checklist not found.",
            "danger",
        )

        return redirect(
            url_for("audit_checklist.index")
        )

    item = item_service.repository.model.query.filter_by(
        id=item_id
    ).first()

    if not item:

        flash(
            "Audit Checklist Item not found.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_checklist.detail",
                audit_checklist_id=audit_checklist_id,
                item_status="inactive",
            )
        )

    if item.audit_checklist_id != audit_checklist_id:

        flash(
            "Invalid Audit Checklist Item.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_checklist.detail",
                audit_checklist_id=audit_checklist_id,
                item_status="inactive",
            )
        )

    try:

        result = item_service.restore(
            item_id
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
            f"Failed to restore Checklist Item: {ex}",
            "danger",
        )

    return redirect(
        url_for(
            "audit_checklist.detail",
            audit_checklist_id=audit_checklist_id,
            item_status="inactive",
        )
    )

# ==========================================================
# EXPORT CHECKLIST ITEMS
# ==========================================================

@audit_checklist_bp.route(
    "/<int:audit_checklist_id>/items/export",
    methods=["GET"],
)
@login_required
def export_items(audit_checklist_id):

    audit_checklist = service.get_by_id(
        audit_checklist_id
    )

    if not audit_checklist:

        flash(
            "Audit Checklist not found.",
            "danger",
        )

        return redirect(
            url_for("audit_checklist.index")
        )

    item_status = request.args.get(
        "item_status",
        "active",
        type=str,
    )

    if item_status == "active":
        item_active_filter = True

    elif item_status == "inactive":
        item_active_filter = False

    else:
        item_status = "all"
        item_active_filter = None

    try:

        items = item_service.get_by_checklist_status(
            audit_checklist_id=audit_checklist_id,
            is_active=item_active_filter,
        )

        from openpyxl import Workbook

        workbook = Workbook()
        worksheet = workbook.active

        worksheet.title = "Checklist Items"

        # ==================================================
        # HEADER
        # ==================================================

        worksheet.append([
            "Checklist Code",
            "Checklist Name",
            "Item No",
            "Question",
            "Description",
            "Required",
            "Sort Order",
            "Status",
        ])

        # ==================================================
        # DATA
        # ==================================================

        for item in items:

            worksheet.append([
                audit_checklist.audit_checklist_code,
                audit_checklist.audit_checklist_name,
                item.item_no,
                item.question,
                item.description or "",
                "Yes" if item.is_required else "No",
                item.sort_order,
                "Active" if item.is_active else "Inactive",
            ])

        # ==================================================
        # COLUMN WIDTH
        # ==================================================

        worksheet.column_dimensions["A"].width = 20
        worksheet.column_dimensions["B"].width = 35
        worksheet.column_dimensions["C"].width = 10
        worksheet.column_dimensions["D"].width = 60
        worksheet.column_dimensions["E"].width = 60
        worksheet.column_dimensions["F"].width = 12
        worksheet.column_dimensions["G"].width = 12
        worksheet.column_dimensions["H"].width = 15

        # ==================================================
        # FILE
        # ==================================================

        output = BytesIO()

        workbook.save(output)

        output.seek(0)

        filename = (
            f"{audit_checklist.audit_checklist_code}"
            f"_checklist_items.xlsx"
        )

        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

    except Exception as ex:

        flash(
            f"Failed to export Checklist Items: {ex}",
            "danger",
        )

        return redirect(
            url_for(
                "audit_checklist.detail",
                audit_checklist_id=audit_checklist_id,
                item_status=item_status,
            )
        )