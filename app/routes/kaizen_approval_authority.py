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

from app.services.kaizen_approval_authority_service import (
    KaizenApprovalAuthorityService,
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

kaizen_approval_authority_bp = Blueprint(
    "kaizen_approval_authority",
    __name__,
    url_prefix="/kaizen-approval-authority",
)


# ==========================================================
# Services
# ==========================================================

approval_authority_service = (
    KaizenApprovalAuthorityService()
)

employee_service = (
    EmployeeService()
)

department_service = (
    DepartmentService()
)


# ==========================================================
# Authorization
# ==========================================================

def _can_manage_authority():

    # ------------------------------------------------------
    # Not authenticated
    # ------------------------------------------------------

    if not current_user.is_authenticated:

        return False


    # ------------------------------------------------------
    # Admin
    # ------------------------------------------------------

    if getattr(
        current_user,
        "is_admin",
        False,
    ):

        return True


    if getattr(
        current_user,
        "role_code",
        None,
    ) == "ADMIN":

        return True


    # ------------------------------------------------------
    # Permission
    # ------------------------------------------------------

    return current_user.has_permission(
        "KAIZEN_APPROVE"
    )


# ==========================================================
# LIST
# ==========================================================

@kaizen_approval_authority_bp.route("/")
@login_required
def index():

    # ==================================================
    # Authorization
    # ==================================================

    if not _can_manage_authority():

        abort(403)


    # ==================================================
    # Get Authorities
    # ==================================================

    authorities = (
        approval_authority_service
        .get_active()
    )


    # ==================================================
    # Render
    # ==================================================

    return render_template(
        "kaizen_approval_authority/list.html",
        authorities=authorities,
    )


# ==========================================================
# CREATE / ASSIGN
# ==========================================================

@kaizen_approval_authority_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
def create():

    # ==================================================
    # Authorization
    # ==================================================

    if not _can_manage_authority():

        abort(403)


    # ==================================================
    # Get Departments
    # ==================================================

    departments = (
        department_service.get_all(
            page=1,
            per_page=1000,
            sort_by="department_name",
            sort_order="asc",
        )
    )


    # ==================================================
    # Get Employees
    # ==================================================

    employees = (
        employee_service.get_all(
            page=1,
            per_page=1000,
            sort_by="full_name",
            sort_order="asc",
        )
    )


    # ==================================================
    # POST
    # ==================================================

    if request.method == "POST":

        department_id = request.form.get(
            "department_id"
        )

        employee_id = request.form.get(
            "employee_id"
        )


        # ==============================================
        # Validate Department
        # ==============================================

        if not department_id:

            flash(
                "Please select a department.",
                "danger",
            )

            return render_template(
                "kaizen_approval_authority/form.html",
                departments=departments.items,
                employees=employees.items,
            )


        # ==============================================
        # Validate Employee
        # ==============================================

        if not employee_id:

            flash(
                "Please select an employee.",
                "danger",
            )

            return render_template(
                "kaizen_approval_authority/form.html",
                departments=departments.items,
                employees=employees.items,
            )


        # ==============================================
        # Convert ID
        # ==============================================

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
                "kaizen_approval_authority/form.html",
                departments=departments.items,
                employees=employees.items,
            )


        # ==============================================
        # Assign Authority
        # ==============================================

        result = (
            approval_authority_service
            .assign(
                department_id=department_id,
                employee_id=employee_id,
                assigned_by=current_user.id,
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

            return redirect(
                url_for(
                    "kaizen_approval_authority.index"
                )
            )


        flash(
            result.message,
            "danger",
        )


    # ==================================================
    # Render
    # ==================================================

    return render_template(
        "kaizen_approval_authority/form.html",
        departments=departments.items,
        employees=employees.items,
    )


# ==========================================================
# REMOVE
# ==========================================================

@kaizen_approval_authority_bp.route(
    "/remove/<int:department_id>/<int:employee_id>",
    methods=["POST"],
)
@login_required
def remove(
    department_id,
    employee_id,
):

    # ==================================================
    # Authorization
    # ==================================================

    if not _can_manage_authority():

        abort(403)


    # ==================================================
    # Remove Authority
    # ==================================================

    result = (
        approval_authority_service
        .remove(
            department_id=department_id,
            employee_id=employee_id,
            removed_by=current_user.id,
        )
    )


    # ==================================================
    # Result
    # ==================================================

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


    # ==================================================
    # Return
    # ==================================================

    return redirect(
        url_for(
            "kaizen_approval_authority.index"
        )
    )