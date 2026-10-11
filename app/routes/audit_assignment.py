from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_login import login_required
from app.core.authorization import permission_required
from app.services.audit_service import AuditService
from app.services.audit_assignment_service import AuditAssignmentService

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.department_repository import DepartmentRepository


audit_assignment_bp = Blueprint(
    "audit_assignment",
    __name__,
    url_prefix="/audits/<int:audit_id>/assignments",
)


audit_service = AuditService()
assignment_service = AuditAssignmentService()

employee_repository = EmployeeRepository()
department_repository = DepartmentRepository()


# ==========================================================
# LIST ASSIGNMENTS
# ==========================================================

@audit_assignment_bp.route("/", methods=["GET"])
@login_required
@permission_required("AUDIT_VIEW")
def index(audit_id):

    audit = audit_service.get_by_id(audit_id)

    if not audit:
        flash(
            "Audit not found.",
            "danger",
        )

        return redirect(
            url_for("audit.index")
        )

    assignments = assignment_service.get_by_audit(
        audit_id
    )

    return render_template(
        "audit_assignment/list.html",
        audit=audit,
        assignments=assignments,
    )


# ==========================================================
# CREATE ASSIGNMENT
# ==========================================================

@audit_assignment_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@permission_required("AUDIT_ASSIGN")
def create(audit_id):

    audit = audit_service.get_by_id(audit_id)

    if not audit:

        flash(
            "Audit not found.",
            "danger",
        )

        return redirect(
            url_for("audit.index")
        )

    # ------------------------------------------------------
    # Get Active Employees
    # ------------------------------------------------------

    employees = employee_repository.get_active()

    # ------------------------------------------------------
    # Get Active Departments
    # ------------------------------------------------------

    departments = department_repository.get_active()

    # ------------------------------------------------------
    # POST
    # ------------------------------------------------------

    if request.method == "POST":

        # --------------------------------------------------
        # Department
        # --------------------------------------------------

        department_id = request.form.get(
            "department_id",
            type=int,
        )

        # --------------------------------------------------
        # Location
        # --------------------------------------------------

        location = request.form.get(
            "location",
            "",
        ).strip()

        # --------------------------------------------------
        # Auditors
        # --------------------------------------------------

        auditor_employee_ids = request.form.getlist(
            "auditor_employee_ids"
        )

        # --------------------------------------------------
        # Convert IDs to Integer
        # --------------------------------------------------

        try:

            auditor_employee_ids = [
                int(employee_id)
                for employee_id in auditor_employee_ids
                if employee_id
            ]

        except (TypeError, ValueError):

            flash(
                "Invalid auditor selection.",
                "danger",
            )

            return render_template(
                "audit_assignment/form.html",
                audit=audit,
                employees=employees,
                departments=departments,
            )

        # --------------------------------------------------
        # Validate Department
        # --------------------------------------------------

        if not department_id:

            flash(
                "Department is required.",
                "danger",
            )

            return render_template(
                "audit_assignment/form.html",
                audit=audit,
                employees=employees,
                departments=departments,
            )

        # --------------------------------------------------
        # Validate Location
        # --------------------------------------------------

        if not location:

            flash(
                "Location is required.",
                "danger",
            )

            return render_template(
                "audit_assignment/form.html",
                audit=audit,
                employees=employees,
                departments=departments,
            )

        # --------------------------------------------------
        # Validate Auditor
        # --------------------------------------------------

        if not auditor_employee_ids:

            flash(
                "Please select at least one auditor.",
                "danger",
            )

            return render_template(
                "audit_assignment/form.html",
                audit=audit,
                employees=employees,
                departments=departments,
            )

        # --------------------------------------------------
        # Create Assignments
        # --------------------------------------------------

        try:

            assignments = assignment_service.create_multiple(
                audit_id=audit_id,
                department_id=department_id,
                auditor_employee_ids=auditor_employee_ids,
                location=location,
            )

            if assignments:

                flash(
                    f"{len(assignments)} auditor "
                    f"assignment(s) created successfully.",
                    "success",
                )

            else:

                flash(
                    "No new assignment was created. "
                    "The selected assignment(s) "
                    "may already exist.",
                    "warning",
                )

            return redirect(
                url_for(
                    "audit_assignment.index",
                    audit_id=audit_id,
                )
            )

        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )

        except Exception as ex:

            flash(
                f"Failed to create audit assignment: {ex}",
                "danger",
            )

    return render_template(
        "audit_assignment/form.html",
        audit=audit,
        employees=employees,
        departments=departments,
    )


# ==========================================================
# DELETE ASSIGNMENT
# ==========================================================

@audit_assignment_bp.route(
    "/<int:assignment_id>/delete",
    methods=["POST"],
)
@login_required
@permission_required("AUDIT_ASSIGN")
def delete(
    audit_id,
    assignment_id,
):

    audit = audit_service.get_by_id(
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

    assignment = assignment_service.get_by_id(
        assignment_id
    )

    if not assignment:

        flash(
            "Audit Assignment not found.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_assignment.index",
                audit_id=audit_id,
            )
        )

    # ------------------------------------------------------
    # Security Check
    # ------------------------------------------------------

    if assignment.audit_id != audit_id:

        flash(
            "Invalid audit assignment.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_assignment.index",
                audit_id=audit_id,
            )
        )

    try:

        assignment_service.delete(
            assignment
        )

        flash(
            "Audit Assignment deleted successfully.",
            "success",
        )

    except Exception as ex:

        flash(
            f"Failed to delete audit assignment: {ex}",
            "danger",
        )

    return redirect(
        url_for(
            "audit_assignment.index",
            audit_id=audit_id,
        )
    )


# ==========================================================
# EDIT ASSIGNMENT
# ==========================================================

@audit_assignment_bp.route(
    "/<int:assignment_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@permission_required("AUDIT_ASSIGN")
def edit(
    audit_id,
    assignment_id,
):

    audit = audit_service.get_by_id(
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

    assignment = assignment_service.get_by_id(
        assignment_id
    )

    if not assignment:

        flash(
            "Audit Assignment not found.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_assignment.index",
                audit_id=audit_id,
            )
        )

    # ------------------------------------------------------
    # Security Check
    # ------------------------------------------------------

    if assignment.audit_id != audit_id:

        flash(
            "Invalid audit assignment.",
            "danger",
        )

        return redirect(
            url_for(
                "audit_assignment.index",
                audit_id=audit_id,
            )
        )

    # ------------------------------------------------------
    # Prevent Edit After Execution Exists
    # ------------------------------------------------------

    if assignment.audit_executions:

        flash(
            "This assignment cannot be edited because "
            "an Audit Execution already exists.",
            "warning",
        )

        return redirect(
            url_for(
                "audit_assignment.index",
                audit_id=audit_id,
            )
        )

    # ------------------------------------------------------
    # Get Active Employees
    # ------------------------------------------------------

    employees = employee_repository.get_active()

    # ------------------------------------------------------
    # Get Active Departments
    # ------------------------------------------------------

    departments = department_repository.get_active()

    # ------------------------------------------------------
    # POST
    # ------------------------------------------------------

    if request.method == "POST":

        # --------------------------------------------------
        # Department
        # --------------------------------------------------

        department_id = request.form.get(
            "department_id",
            type=int,
        )

        # --------------------------------------------------
        # Location
        # --------------------------------------------------

        location = request.form.get(
            "location",
            "",
        ).strip()

        # --------------------------------------------------
        # Auditor
        # --------------------------------------------------

        auditor_employee_id = request.form.get(
            "auditor_employee_id",
            type=int,
        )

        # --------------------------------------------------
        # Validate Department
        # --------------------------------------------------

        if not department_id:

            flash(
                "Department is required.",
                "danger",
            )

            return render_template(
                "audit_assignment/edit.html",
                audit=audit,
                assignment=assignment,
                employees=employees,
                departments=departments,
            )

        # --------------------------------------------------
        # Validate Location
        # --------------------------------------------------

        if not location:

            flash(
                "Location is required.",
                "danger",
            )

            return render_template(
                "audit_assignment/edit.html",
                audit=audit,
                assignment=assignment,
                employees=employees,
                departments=departments,
            )

        # --------------------------------------------------
        # Validate Auditor
        # --------------------------------------------------

        if not auditor_employee_id:

            flash(
                "Please select an auditor.",
                "danger",
            )

            return render_template(
                "audit_assignment/edit.html",
                audit=audit,
                assignment=assignment,
                employees=employees,
                departments=departments,
            )

        # --------------------------------------------------
        # Update Assignment
        # --------------------------------------------------

        try:

            assignment_service.update(
                assignment=assignment,
                department_id=department_id,
                auditor_employee_id=auditor_employee_id,
                location=location,
            )

            flash(
                "Audit Assignment updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "audit_assignment.index",
                    audit_id=audit_id,
                )
            )

        except ValueError as ex:

            flash(
                str(ex),
                "danger",
            )

        except Exception as ex:

            flash(
                f"Failed to update audit assignment: {ex}",
                "danger",
            )

    return render_template(
        "audit_assignment/edit.html",
        audit=audit,
        assignment=assignment,
        employees=employees,
        departments=departments,
    )