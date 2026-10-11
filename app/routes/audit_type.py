from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    url_for,
    send_file,
)

from flask_login import login_required

from app.services.audit_type_service import AuditTypeService

from io import BytesIO


audit_type_bp = Blueprint(
    "audit_type",
    __name__,
    url_prefix="/audit_types",
)


service = AuditTypeService()


@audit_type_bp.route("/")
@login_required
def index():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int
    )

    sort_by = request.args.get(
        "sort",
        "audit_type_code"
    )

    sort_order = request.args.get(
        "order",
        "asc"
    )

    is_active_param = request.args.get(
        "is_active",
        "true"
    ).lower()

    if is_active_param == "true":

        is_active = True

    elif is_active_param == "false":

        is_active = False

    else:

        is_active = None

    audit_types = service.get_all(
        keyword=keyword,
        is_active=is_active,
        page=page,
        per_page=10,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "audit_type/list.html",
        audit_types=audit_types,
        keyword=keyword,
        is_active=is_active_param,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@audit_type_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():

    if request.method == "GET":

        return render_template(
            "audit_type/form.html",
            audit_type=None,
        )

    audit_type_code = request.form.get(
        "audit_type_code",
        ""
    ).strip()

    audit_type_name = request.form.get(
        "audit_type_name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:

        service.create(
            audit_type_code=audit_type_code,
            audit_type_name=audit_type_name,
            description=description,
        )

        flash(
            "Audit Type created successfully.",
            "success"
        )

        return redirect(
            url_for("audit_type.index")
        )

    except ValueError as e:

        flash(
            str(e),
            "danger"
        )

        return render_template(
            "audit_type/form.html",
            audit_type=None,
        )

    except Exception:

        flash(
            "Failed to create Audit Type.",
            "danger"
        )

        return render_template(
            "audit_type/form.html",
            audit_type=None,
        )


@audit_type_bp.route(
    "/edit/<int:audit_type_id>",
    methods=["GET", "POST"]
)
@login_required
def edit(audit_type_id):

    audit_type = service.get_by_id(
        audit_type_id
    )

    if not audit_type:

        flash(
            "Audit Type not found.",
            "danger"
        )

        return redirect(
            url_for("audit_type.index")
        )

    if request.method == "GET":

        return render_template(
            "audit_type/form.html",
            audit_type=audit_type,
        )

    audit_type_name = request.form.get(
        "audit_type_name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:

        service.update(
            audit_type=audit_type,
            audit_type_name=audit_type_name,
            description=description,
        )

        flash(
            "Audit Type updated successfully.",
            "success"
        )

        return redirect(
            url_for("audit_type.index")
        )

    except ValueError as ex:

        flash(
            str(ex),
            "danger"
        )

        return render_template(
            "audit_type/form.html",
            audit_type=audit_type,
        )

    except Exception as ex:

        flash(
            f"Failed to update Audit Type. {ex}",
            "danger"
        )

        return render_template(
            "audit_type/form.html",
            audit_type=audit_type,
        )

@audit_type_bp.route(
    "/delete/<int:audit_type_id>",
    methods=["POST"]
)
@login_required
def delete(audit_type_id):

    audit_type = service.get_by_id(
        audit_type_id
    )

    if audit_type is None:

        flash(
            "Audit Type not found.",
            "danger",
        )

        return redirect(
            url_for("audit_type.index")
        )

    try:

        service.delete(audit_type)

        flash(
            "Audit Type deleted successfully.",
            "success",
        )

    except ValueError as ex:

        flash(
            str(ex),
            "danger",
        )

    except Exception as ex:

        flash(
            f"Failed to delete Audit Type. {ex}",
            "danger",
        )

    return redirect(
        url_for("audit_type.index")
    )


@audit_type_bp.route("/export")
@login_required
def export():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    sort_by = request.args.get(
        "sort",
        "audit_type_code"
    )

    sort_order = request.args.get(
        "order",
        "asc"
    )

    is_active_param = request.args.get(
        "is_active",
        "true"
    ).lower()

    if is_active_param == "true":

        is_active = True

    elif is_active_param == "false":

        is_active = False

    else:

        is_active = None

    workbook = service.export_excel(
        keyword=keyword,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Audit_Type.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


@audit_type_bp.route(
    "/restore/<int:audit_type_id>",
    methods=["POST"]
)
@login_required
def restore(audit_type_id):

    result = service.restore(
        audit_type_id
    )

    flash(
        result.message,
        "success" if result.success else "danger"
    )

    return redirect(
        url_for("audit_type.index")
    )