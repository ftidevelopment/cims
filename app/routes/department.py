from flask import Blueprint, render_template,request,redirect,flash,url_for
from app.core.authorization import permission_required
from app.services.department_service import DepartmentService
from flask_login import login_required
from io import BytesIO
from flask import send_file

department_bp = Blueprint(
    "department",
    __name__,
    url_prefix="/departments",
)

service = DepartmentService()


@department_bp.route("/")
@login_required
@permission_required("DEPARTMENT_VIEW")
def index():

    keyword = request.args.get("keyword", "").strip()

    page = request.args.get("page", 1, type=int)

    sort_by = request.args.get(
        "sort",
        "department_code"
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

    departments = service.get_all(
        keyword=keyword,
        is_active=is_active,
        page=page,
        per_page=10,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "department/list.html",
        departments=departments,
        keyword=keyword,
        is_active=is_active_param,       
        sort_by=sort_by,
        sort_order=sort_order,
        next_sort_order=next_sort_order
    )

@department_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("DEPARTMENT_CREATE")
def create():

    if request.method == "GET":

        return render_template(
            "department/form.html",
            department=None,
        )

    department_code = request.form.get(
        "department_code"
    ).strip()

    department_name = request.form.get(
        "department_name"
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:

        service.create(
            department_code=department_code,
            department_name=department_name,
            description=description,
        )

        flash(
            "Department created successfully.",
            "success"
        )

        return redirect(
            url_for("department.index")
        )

    except ValueError as e:

        flash(str(e), "danger")

        return render_template(
            "department/form.html",
            department=None,
        )

    except Exception:

        flash(
            "Failed to create department.",
            "danger"
        )

        return render_template(
            "department/form.html",
            department=None,
        )


@department_bp.route("/edit/<int:department_id>", methods=["GET", "POST"])
@login_required
@permission_required("DEPARTMENT_EDIT")
def edit(department_id):

    department = service.get_by_id(department_id)

    if not department:

        flash(
            "Department not found.",
            "danger"
        )

        return redirect(
            url_for("department.index")
        )

    if request.method == "GET":

        return render_template(
            "department/form.html",
            department=department,
        )

    department_name = request.form.get(
        "department_name"
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:

        service.update(
            department=department,
            department_name=department_name,
            description=description,
        )

        flash(
            "Department updated successfully.",
            "success"
        )

        return redirect(
            url_for("department.index")
        )

    except Exception:

        flash(
            "Failed to update department.",
            "danger"
        )

        return render_template(
            "department/form.html",
            department=department,
        )


@department_bp.route("/delete/<int:department_id>", methods=["POST"])
@login_required
@permission_required("DEPARTMENT_DELETE")
def delete(department_id):

    department = service.get_by_id(department_id)

    if department is None:

        flash(
            "Department not found.",
            "danger",
        )

        return redirect(
            url_for("department.index")
        )

    try:

        service.delete(department)

        flash(
            "Department deleted successfully.",
            "success",
        )

    except ValueError as ex:

        flash(
            str(ex),
            "danger",
        )

    except Exception as ex:

        flash(
            f"Failed to delete department. {ex}",
            "danger",
        )

    return redirect(
        url_for("department.index")
    )

def next_sort_order(current_sort, current_order, column):
    if current_sort == column and current_order == "asc":
        return "desc"
    return "asc"


@department_bp.route("/export")
@login_required
def export():

    keyword = request.args.get("keyword", "").strip()

    sort_by = request.args.get(
        "sort",
        "department_code"
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
        download_name="Department.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@department_bp.route(
    "/restore/<int:department_id>",
    methods=["POST"]
)
@login_required
def restore(department_id):

    result = service.restore(department_id)

    flash(
        result.message,
        "success" if result.success else "danger"
    )

    return redirect(url_for("department.index"))