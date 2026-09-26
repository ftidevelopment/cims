from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    login_required,
    current_user,
)

from app.core.authorization import (
    permission_required,
)

from app.services.problem_assignment_authority_service import (
    ProblemAssignmentAuthorityService,
)

from app.services.department_service import (
    DepartmentService,
)

from app.services.employee_service import (
    EmployeeService,
)


problem_assignment_authority_bp = Blueprint(
    "problem_assignment_authority",
    __name__,
    url_prefix="/problem-assignment-authorities",
)


authority_service = (
    ProblemAssignmentAuthorityService()
)

department_service = DepartmentService()
employee_service = EmployeeService()


# ==================================================
# List
# ==================================================

@problem_assignment_authority_bp.route("/")
@login_required
@permission_required(
    "PROBLEM_ASSIGNMENT_AUTHORITY_VIEW"
)
def index():

    departments = (
        department_service.get_all(
            page=1,
            per_page=1000,
            sort_by="department_name",
            sort_order="asc",
        )
    )

    authorities = (
        authority_service.get_active()
    )

    return render_template(
        "problem_assignment_authority/list.html",
        departments=departments.items,
        authorities=authorities,
    )


# ==================================================
# Create / Assign
# ==================================================

@problem_assignment_authority_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@permission_required(
    "PROBLEM_ASSIGNMENT_AUTHORITY_CREATE"
)
def create():

    # ==================================================
    # POST
    # ==================================================

    if request.method == "POST":

        department_id = request.form.get(
            "department_id",
            type=int,
        )

        employee_id = request.form.get(
            "employee_id",
            type=int,
        )

        if not department_id:

            flash(
                "Please select a department.",
                "danger",
            )

            return redirect(
                url_for(
                    "problem_assignment_authority.create"
                )
            )

        if not employee_id:

            flash(
                "Please select an employee.",
                "danger",
            )

            return redirect(
                url_for(
                    "problem_assignment_authority.create"
                )
            )

        result = authority_service.assign(
            department_id=department_id,
            employee_id=employee_id,
            created_by=current_user.id,
        )

        flash(
            result.message,
            "success"
            if result.success
            else "danger",
        )

        if result.success:

            return redirect(
                url_for(
                    "problem_assignment_authority.index"
                )
            )

    # ==================================================
    # GET
    # ==================================================

    departments = (
        department_service.get_all(
            page=1,
            per_page=1000,
            sort_by="department_name",
            sort_order="asc",
        )
    )

    employees = (
        employee_service.get_all(
            page=1,
            per_page=1000,
            sort_by="full_name",
            sort_order="asc",
        )
    )

    # ==================================================
    # Only ACTIVE employees with User Account
    # ==================================================

    eligible_employees = []

    for employee in employees.items:

        if not employee.is_active:
            continue

        if not employee.user:
            continue

        eligible_employees.append(
            employee
        )

    return render_template(
        "problem_assignment_authority/form.html",
        departments=departments.items,
        employees=eligible_employees,
    )


# ==================================================
# Remove
# ==================================================

@problem_assignment_authority_bp.route(
    "/remove/<int:department_id>/<int:employee_id>",
    methods=["POST"],
)
@login_required
@permission_required(
    "PROBLEM_ASSIGNMENT_AUTHORITY_DELETE"
)
def remove(
    department_id,
    employee_id,
):

    result = authority_service.remove(
        department_id=department_id,
        employee_id=employee_id,
        updated_by=current_user.id,
    )

    flash(
        result.message,
        "success"
        if result.success
        else "danger",
    )

    return redirect(
        url_for(
            "problem_assignment_authority.index"
        )
    )


# ==================================================
# Restore
# ==================================================

@problem_assignment_authority_bp.route(
    "/restore/<int:department_id>/<int:employee_id>",
    methods=["POST"],
)
@login_required
@permission_required(
    "PROBLEM_ASSIGNMENT_AUTHORITY_CREATE"
)
def restore(
    department_id,
    employee_id,
):

    result = authority_service.restore(
        department_id=department_id,
        employee_id=employee_id,
        updated_by=current_user.id,
    )

    flash(
        result.message,
        "success"
        if result.success
        else "danger",
    )

    return redirect(
        url_for(
            "problem_assignment_authority.index"
        )
    )