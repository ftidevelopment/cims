from flask import Blueprint, render_template,request,redirect,flash,url_for
from app.core.authorization import permission_required
from app.services.employee_service import EmployeeService
from flask_login import login_required
from io import BytesIO
from flask import send_file
from app.services.line_service import LineService

employee_bp = Blueprint(
    "employee",
    __name__,
    url_prefix="/employees",
)

service = EmployeeService()


@employee_bp.route("/")
@login_required
@permission_required("EMPLOYEE_VIEW")
def index():

    keyword = request.args.get("keyword", "").strip()

    page = request.args.get("page", 1, type=int)

    sort_by = request.args.get(
        "sort",
        "nik"
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

    employees = service.get_all(       
        keyword=keyword,
        is_active=is_active,
        page=page,
        per_page=10,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "employee/list.html",
        employees=employees,
        keyword=keyword,
        is_active=is_active_param,       
        sort_by=sort_by,
        sort_order=sort_order,     
    )



@employee_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("EMPLOYEE_CREATE")
def create():

    if request.method == "GET":

        departments = service.get_departments()

        return render_template(
            "employee/form.html",
            employee=None,
            departments=departments,
        )

    nik = request.form.get(
        "nik"
    ).strip()

    full_name = request.form.get(
        "full_name"
    ).strip()

    department_id = request.form.get(
        "department_id",
        type=int
    )

    email = request.form.get(
        "email"
    ).strip()

    phone_number = request.form.get(
        "phone_number"
    ).strip()

    telegram_chat_id = request.form.get(
        "telegram_chat_id"
    ).strip()
    line_user_id = request.form.get(
        "line_user_id"
    ).strip()


    try:

        service.create(
            nik=nik,
            full_name=full_name,
            department_id=department_id,
            email=email,
            phone_number=phone_number,
            telegram_chat_id=telegram_chat_id,
            line_user_id=line_user_id,
        )

        flash(
            "Employee created successfully.",
            "success"
        )

        return redirect(
            url_for("employee.index")
        )

    except ValueError as e:

        departments = service.get_departments()

        flash(
            str(e),
            "danger"
        )

        return render_template(
            "employee/form.html",
            employee=None,
            departments=departments,
        )

    except Exception:

        departments = service.get_departments()

        flash(
            "Failed to create employee.",
            "danger"
        )

        return render_template(
            "employee/form.html",
            employee=None,
            departments=departments,
        )

@employee_bp.route("/edit/<int:employee_id>", methods=["GET", "POST"])
@login_required
@permission_required("EMPLOYEE_EDIT")
def edit(employee_id):

    employee = service.get_by_id(employee_id)

    if not employee:

        flash(
            "Employee not found.",
            "danger"
        )

        return redirect(
            url_for("employee.index")
        )

    if request.method == "GET":

        departments = service.get_departments()

        return render_template(
            "employee/form.html",
            employee=employee,
            departments=departments,
        )

    nik = request.form.get(
        "nik"
    ).strip()

    full_name = request.form.get(
        "full_name"
    ).strip()

    department_id = request.form.get(
        "department_id",
        type=int
    )

    email = request.form.get(
        "email"
    ).strip()

    phone_number = request.form.get(
        "phone_number"
    ).strip()

    telegram_chat_id = request.form.get(
        "telegram_chat_id"
    ).strip()
    line_user_id = request.form.get(
        "line_user_id"
    ).strip()

    try:

        service.update(
            employee=employee,
            nik=nik,
            full_name=full_name,
            department_id=department_id,
            email=email,
            phone_number=phone_number,
            telegram_chat_id=telegram_chat_id,
            line_user_id=line_user_id,
        )

        flash(
            "Employee updated successfully.",
            "success"
        )

        return redirect(
            url_for("employee.index")
        )

    except ValueError as e:

        departments = service.get_departments()

        flash(
            str(e),
            "danger"
        )

        return render_template(
            "employee/form.html",
            employee=employee,
            departments=departments,
        )

    except Exception:

        departments = service.get_departments()

        flash(
            "Failed to update employee.",
            "danger"
        )

        return render_template(
            "employee/form.html",
            employee=employee,
            departments=departments,
        )


@employee_bp.route("/delete/<int:employee_id>", methods=["POST"])
@login_required
@permission_required("EMPLOYEE_DELETE")
def delete(employee_id):

    employee = service.get_by_id(employee_id)

    if employee is None:

        flash(
            "Employee not found.",
            "danger",
        )

        return redirect(
            url_for("employee.index")
        )

    try:

        service.delete(employee)

        flash(
            "Employee deleted successfully.",
            "success",
        )

    except ValueError as ex:

        flash(
            str(ex),
            "danger",
        )

    except Exception as ex:

        flash(
            f"Failed to delete employee. {ex}",
            "danger",
        )

    return redirect(
        url_for("employee.index")
    )


@employee_bp.route("/export")
@login_required
def export():

    keyword = request.args.get("keyword", "").strip()

    sort_by = request.args.get(
        "sort",
        "nik"
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
        download_name="Employee.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@employee_bp.route(
    "/restore/<int:employee_id>",
    methods=["POST"]
)
@login_required
def restore(employee_id):
    result = service.restore(employee_id)

    flash(
        result.message,
        "success" if result.success else "danger"
    )

    return redirect(url_for("employee.index"))


@employee_bp.route(
    "/test-line/<int:employee_id>"
)
@login_required
def test_line(employee_id):

    employee = service.get_by_id(
        employee_id
    )

    if not employee:

        flash(
            "Employee not found.",
            "danger"
        )

        return redirect(
            url_for("employee.index")
        )

    if not employee.line_user_id:

        flash(
            "LINE User ID is not registered for this employee.",
            "danger"
        )

        return redirect(
            url_for("employee.index")
        )

    try:

        LineService.send_message(
            employee.line_user_id,
            f"Halo {employee.full_name}, "
            "ini adalah test notification dari CIMS."
        )

        flash(
            "LINE test message sent successfully.",
            "success"
        )

    except Exception as ex:

        flash(
            f"Failed to send LINE message. {ex}",
            "danger"
        )

    return redirect(
        url_for("employee.index")
    )