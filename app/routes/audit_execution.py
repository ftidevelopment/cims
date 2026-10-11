
from datetime import datetime, date
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user

from app.services.audit_execution_service import (
    AuditExecutionService,
)
from app.services.audit_execution_item_service import (
    AuditExecutionItemService,
)
from app.services.audit_assignment_service import (
    AuditAssignmentService,
)
from app.services.audit_checklist_service import (
    AuditChecklistService,
)
from app.services.audit_service import AuditService


# ==========================================================
# BLUEPRINT
# ==========================================================

audit_execution_bp = Blueprint(
    "audit_execution",
    __name__,
    url_prefix="/audits",
)


# ==========================================================
# SERVICES
# ==========================================================

service = AuditExecutionService()
item_service = AuditExecutionItemService()
assignment_service = AuditAssignmentService()
checklist_service = AuditChecklistService()
audit_service = AuditService()


# ==========================================================
# AUTHORIZATION HELPERS
# ==========================================================

ADMIN_ROLES = {"ADMIN", "AUDIT_ADMIN"}


def _is_audit_admin():
    """
    ADMIN dan AUDIT_ADMIN dapat mengakses seluruh
    Audit Execution.
    """
    role_code = (
        getattr(current_user, "role_code", "") or ""
    ).strip().upper()

    return role_code in ADMIN_ROLES


def _has_audit_permission(permission_code):
    """
    Admin audit mendapat akses penuh.
    Pengguna lain harus memiliki permission terkait.
    """
    if _is_audit_admin():
        return True

    return current_user.has_permission(permission_code)


def audit_permission_required(permission_code):
    """
    Pengganti permission_required khusus modul Audit
    agar ADMIN dan AUDIT_ADMIN dapat melewati
    pemeriksaan permission individual.
    """
    def decorator(view_function):
        @wraps(view_function)
        @login_required
        def wrapped_view(*args, **kwargs):
            if not _has_audit_permission(permission_code):
                flash(
                    "You do not have permission to access "
                    "this Audit function.",
                    "danger",
                )
                return redirect(url_for("dashboard.index"))

            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator


def _owns_assignment(assignment):
    """
    Admin boleh mengakses semua assignment.
    Auditor biasa hanya boleh mengakses assignment
    milik employee_id miliknya sendiri.
    """
    if not assignment:
        return False

    if _is_audit_admin():
        return True

    employee_id = getattr(
        current_user,
        "employee_id",
        None,
    )

    return (
        employee_id is not None
        and assignment.auditor_employee_id == employee_id
    )


def _execution_is_accessible(
    execution,
    audit_id,
):
    """
    Memastikan execution:
    1. Ada.
    2. Memiliki assignment.
    3. Berasal dari audit pada URL.
    4. Dimiliki auditor yang login, kecuali admin.
    """
    if not execution:
        return False

    assignment = getattr(
        execution,
        "audit_assignment",
        None,
    )

    if not assignment:
        return False

    if assignment.audit_id != audit_id:
        return False

    return _owns_assignment(assignment)


def _deny_execution_access(audit_id):
    flash(
        "You are not authorized to access this "
        "Audit Execution.",
        "danger",
    )
    return redirect(
        url_for(
            "audit_execution.index",
            audit_id=audit_id,
        )
    )


def _get_assignments_for_current_user(audit_id):
    """
    Admin mendapatkan seluruh assignment.
    Auditor biasa hanya mendapatkan assignment sendiri.
    """
    assignments = assignment_service.get_by_audit(
        audit_id
    )

    if _is_audit_admin():
        return assignments

    employee_id = getattr(
        current_user,
        "employee_id",
        None,
    )

    if employee_id is None:
        return []

    return [
        assignment
        for assignment in assignments
        if assignment.auditor_employee_id == employee_id
    ]


# ==========================================================
# EXECUTION LIST
# ==========================================================

@audit_execution_bp.route(
    "/<int:audit_id>/executions",
    methods=["GET"],
)
@audit_permission_required("AUDIT_VIEW")
def index(audit_id):
    audit = audit_service.get_by_id(audit_id)

    if not audit:
        flash("Audit not found.", "danger")
        return redirect(url_for("audit.index"))

    # Hanya assignment yang boleh dilihat pengguna.
    assignments = _get_assignments_for_current_user(
        audit_id
    )

    executions = []

    for assignment in assignments:
        assignment_executions = service.get_by_assignment(
            assignment.id
        )

        executions.extend(
            execution
            for execution in assignment_executions
            if _execution_is_accessible(
                execution,
                audit_id,
            )
        )

    executions.sort(
        key=lambda execution: (
            execution.execution_date
            or date.min,
            execution.created_at
            or datetime.min,
        ),
        reverse=True,
    )

    return render_template(
        "audit_execution/index.html",
        audit=audit,
        assignments=assignments,
        executions=executions,
    )


# ==========================================================
# CREATE EXECUTION
# ==========================================================

@audit_execution_bp.route(
    "/<int:audit_id>/executions/create",
    methods=["GET", "POST"],
)
@audit_permission_required("AUDIT_EXECUTE")
def create(audit_id):
    audit = audit_service.get_by_id(audit_id)

    if not audit:
        flash("Audit not found.", "danger")
        return redirect(url_for("audit.index"))

    selected_assignment_id = request.args.get(
        "assignment_id",
        type=int,
    )

    assignments = _get_assignments_for_current_user(
        audit_id
    )

    checklists = checklist_service.get_all(
        is_active=True,
        page=1,
        per_page=1000,
        sort_by="audit_checklist_name",
        sort_order="asc",
    )

    if request.method == "POST":
        audit_assignment_id = request.form.get(
            "audit_assignment_id",
            type=int,
        )
        selected_assignment_id = audit_assignment_id

        audit_checklist_id = request.form.get(
            "audit_checklist_id",
            type=int,
        )

        execution_date = request.form.get(
            "execution_date",
            "",
        ).strip()

        remark = request.form.get(
            "remark",
            "",
        ).strip()

        # Assignment harus berasal dari audit yang benar
        # dan boleh diakses oleh pengguna saat ini.
        assignment = next(
            (
                item
                for item in assignments
                if item.id == audit_assignment_id
            ),
            None,
        )

        if not assignment or not _owns_assignment(assignment):
            flash(
                "Invalid Audit Assignment or access denied.",
                "danger",
            )
            return render_template(
                "audit_execution/create.html",
                audit=audit,
                assignments=assignments,
                checklists=checklists,
                selected_assignment_id=selected_assignment_id,
            )

        if not audit_checklist_id:
            flash("Please select an audit checklist.", "danger")
            return render_template(
                "audit_execution/create.html",
                audit=audit,
                assignments=assignments,
                checklists=checklists,
                selected_assignment_id=selected_assignment_id,
            )

        if execution_date:
            try:
                parsed_date = datetime.strptime(
                    execution_date,
                    "%Y-%m-%d",
                ).date()
            except ValueError:
                flash("Invalid execution date.", "danger")
                return render_template(
                    "audit_execution/create.html",
                    audit=audit,
                    assignments=assignments,
                    checklists=checklists,
                    selected_assignment_id=selected_assignment_id,
                )
        else:
            parsed_date = date.today()

        result = service.create(
            audit_assignment_id=audit_assignment_id,
            audit_checklist_id=audit_checklist_id,
            execution_date=parsed_date,
            remark=remark or None,
        )

        if result.success:
            flash(result.message, "success")
            return redirect(
                url_for(
                    "audit_execution.detail",
                    audit_id=audit.id,
                    execution_id=result.data.id,
                )
            )

        flash(result.message, "danger")

    # Jika assignment dari URL bukan milik pengguna,
    # jangan biarkan form memilih assignment tersebut.
    if (
        selected_assignment_id is not None
        and not any(
            item.id == selected_assignment_id
            for item in assignments
        )
    ):
        selected_assignment_id = None

    return render_template(
        "audit_execution/create.html",
        audit=audit,
        assignments=assignments,
        checklists=checklists,
        selected_assignment_id=selected_assignment_id,
    )


# ==========================================================
# EXECUTION DETAIL / RUN CHECKLIST
# ==========================================================

@audit_execution_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>",
    methods=["GET"],
)
@audit_permission_required("AUDIT_VIEW")
def detail(audit_id, execution_id):
    audit = audit_service.get_by_id(audit_id)

    if not audit:
        flash("Audit not found.", "danger")
        return redirect(url_for("audit.index"))

    execution = service.get_by_id(execution_id)

    if not execution:
        flash("Audit Execution not found.", "danger")
        return redirect(
            url_for(
                "audit_execution.index",
                audit_id=audit_id,
            )
        )

    if not _execution_is_accessible(
        execution,
        audit_id,
    ):
        return _deny_execution_access(audit_id)

    items = item_service.get_by_execution(
        execution.id
    )

    return render_template(
        "audit_execution/detail.html",
        audit=audit,
        execution=execution,
        items=items,
    )


# ==========================================================
# START EXECUTION
# ==========================================================

@audit_execution_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/start",
    methods=["POST"],
)
@audit_permission_required("AUDIT_EXECUTE")
def start(audit_id, execution_id):
    execution = service.get_by_id(execution_id)

    if not execution:
        flash("Audit Execution not found.", "danger")
        return redirect(
            url_for(
                "audit_execution.index",
                audit_id=audit_id,
            )
        )

    if not _execution_is_accessible(
        execution,
        audit_id,
    ):
        return _deny_execution_access(audit_id)

    result = service.start(execution_id)

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(
        url_for(
            "audit_execution.detail",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )


# ==========================================================
# SAVE CHECKLIST RESULTS
# ==========================================================

@audit_execution_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/save",
    methods=["POST"],
)
@audit_permission_required("AUDIT_EXECUTE")
def save(audit_id, execution_id):
    execution = service.get_by_id(execution_id)

    if not execution:
        flash("Audit Execution not found.", "danger")
        return redirect(
            url_for(
                "audit_execution.index",
                audit_id=audit_id,
            )
        )

    if not _execution_is_accessible(
        execution,
        audit_id,
    ):
        return _deny_execution_access(audit_id)

    items = item_service.get_by_execution(
        execution_id
    )

    items_data = []

    for item in items:
        result_value = request.form.get(
            f"result_{item.id}"
        )

        remark = request.form.get(
            f"remark_{item.id}",
            "",
        ).strip()

        items_data.append(
            {
                "item_id": item.id,
                "result": result_value,
                "remark": remark or None,
            }
        )

    result = item_service.update_multiple(
        items_data
    )

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(
        url_for(
            "audit_execution.detail",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )


# ==========================================================
# COMPLETE EXECUTION
# ==========================================================

@audit_execution_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/complete",
    methods=["POST"],
)
@audit_permission_required("AUDIT_EXECUTE")
def complete(audit_id, execution_id):
    execution = service.get_by_id(execution_id)

    if not execution:
        flash("Audit Execution not found.", "danger")
        return redirect(
            url_for(
                "audit_execution.index",
                audit_id=audit_id,
            )
        )

    if not _execution_is_accessible(
        execution,
        audit_id,
    ):
        return _deny_execution_access(audit_id)

    result = service.complete(execution_id)

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(
        url_for(
            "audit_execution.detail",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )
