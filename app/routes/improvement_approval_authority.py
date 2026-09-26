from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)

from flask_login import (
    login_required,
    current_user,
)

from app.services.improvement_approval_authority_service import (
    ImprovementApprovalAuthorityService,
)

from app.services.employee_service import (
    EmployeeService,
)

from app.services.department_service import (
    DepartmentService,
)


# ==========================================================
# Blueprint
# ==========================================================

improvement_approval_authority_bp = Blueprint(
    "improvement_approval_authority",
    __name__,
    url_prefix="/improvement-approval-authority",
)


# ==========================================================
# Services
# ==========================================================

approval_authority_service = (
    ImprovementApprovalAuthorityService()
)

employee_service = (
    EmployeeService()
)

department_service = (
    DepartmentService()
)


# ==========================================================
# ADMIN CHECK
# ==========================================================

def admin_required():

    is_admin = (
        getattr(
            current_user,
            "is_admin",
            False,
        )
        or getattr(
            current_user,
            "role_code",
            None,
        ) == "ADMIN"
    )

    if not is_admin:

        abort(403)


# ==========================================================
# LIST
# ==========================================================

@improvement_approval_authority_bp.route(
    "/",
)
@login_required
def index():

    # ==============================================
    # Admin Only
    # ==============================================

    admin_required()

    # ==============================================
    # Get Active Authorities
    # ==============================================

    authorities = (
        approval_authority_service
        .get_active()
    )

    # ==============================================
    # Render
    # ==============================================

    return render_template(
        "improvement_approval_authority/list.html",
        authorities=authorities,
    )


# ==========================================================
# CREATE
# ==========================================================

@improvement_approval_authority_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
def create():

    # ==============================================
    # Admin Only
    # ==============================================

    admin_required()

    # ==============================================
    # Get Departments
    # ==============================================

    departments = (
        department_service.get_all(
            page=1,
            per_page=1000,
            sort_by="department_name",
            sort_order="asc",
        )
    )

    # ==============================================
    # Get Employees
    # ==============================================

    employees = (
        employee_service.get_all(
            page=1,
            per_page=1000,
            sort_by="full_name",
            sort_order="asc",
        )
    )

    # ==============================================
    # POST
    # ==============================================

    if request.method == "POST":

        department_id = (
            request.form.get(
                "department_id"
            )
        )

        employee_id = (
            request.form.get(
                "employee_id"
            )
        )

        # ==========================================
        # Validate Department
        # ==========================================

        if not department_id:

            flash(
                "Please select a department.",
                "danger",
            )

            return render_template(
                "improvement_approval_authority/form.html",
                departments=departments.items,
                employees=employees.items,
            )

        # ==========================================
        # Validate Employee
        # ==========================================

        if not employee_id:

            flash(
                "Please select an employee.",
                "danger",
            )

            return render_template(
                "improvement_approval_authority/form.html",
                departments=departments.items,
                employees=employees.items,
            )

        # ==========================================
        # Convert ID
        # ==========================================

        try:

            department_id = int(
                department_id
            )

            employee_id = int(
                employee_id
            )

        except ValueError:

            flash(
                "Invalid department or employee.",
                "danger",
            )

            return render_template(
                "improvement_approval_authority/form.html",
                departments=departments.items,
                employees=employees.items,
            )

        # ==========================================
        # Assign Authority
        # ==========================================

        result = (
            approval_authority_service
            .assign(
                department_id=department_id,
                employee_id=employee_id,
                assigned_by=current_user.id,
            )
        )

        # ==========================================
        # Result
        # ==========================================

        if result.success:

            flash(
                result.message,
                "success",
            )

            return redirect(
                url_for(
                    "improvement_approval_authority.index"
                )
            )

        flash(
            result.message,
            "danger",
        )

    # ==============================================
    # Render
    # ==============================================

    return render_template(
        "improvement_approval_authority/form.html",
        departments=departments.items,
        employees=employees.items,
    )


# ==========================================================
# REMOVE
# ==========================================================

@improvement_approval_authority_bp.route(
    "/remove/<int:department_id>/<int:employee_id>",
    methods=["POST"],
)
@login_required
def remove(
    department_id,
    employee_id,
):

    # ==============================================
    # Admin Only
    # ==============================================

    admin_required()

    # ==============================================
    # Remove Authority
    # ==============================================

    result = (
        approval_authority_service
        .remove(
            department_id=department_id,
            employee_id=employee_id,
            removed_by=current_user.id,
        )
    )

    # ==============================================
    # Result
    # ==============================================

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

    # ==============================================
    # Redirect
    # ==============================================

    return redirect(
        url_for(
            "improvement_approval_authority.index"
        )
    )