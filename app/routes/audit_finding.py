from datetime import date, datetime
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask import abort
from flask_login import current_user, login_required
from app.repositories.audit_execution_repository import (
    AuditExecutionRepository,
)
from app.repositories.audit_execution_item_repository import (
    AuditExecutionItemRepository,
)
from app.repositories.employee_repository import EmployeeRepository
from app.services.audit_finding_service import AuditFindingService
from app.services.audit_service import AuditService
from app.services.audit_finding_attachment_service import (
    AuditFindingAttachmentService
)
audit_finding_bp = Blueprint(
    "audit_finding",
    __name__,
    url_prefix="/audits",
)
# ============================================================
# Service / Repository
# ============================================================
audit_service = AuditService()
finding_service = AuditFindingService()
attachment_service = AuditFindingAttachmentService()
execution_repository = AuditExecutionRepository()
execution_item_repository = AuditExecutionItemRepository()
employee_repository = EmployeeRepository()
# ============================================================
# Helper
# ============================================================
def _get_audit_and_execution(audit_id, execution_id):
    """
    Validate that the Audit Execution belongs to the Audit.
    """
    audit = audit_service.get_by_id(audit_id)
    if not audit:
        flash("Audit not found.", "danger")
        return None, None
    execution = execution_repository.get_by_id(execution_id)
    if not execution:
        flash("Audit execution not found.", "danger")
        return audit, None
    if execution.audit_assignment.audit_id != audit_id:
        flash(
            "Audit execution does not belong to this audit.",
            "danger",
        )
        return audit, None
    return audit, execution
def _parse_date(value):
    """
    Convert HTML date value to Python date.
    """
    if not value:
        return None
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()
    except ValueError:
        raise ValueError(
            "Invalid date format."
        )
# ============================================================
# Finding Access Control
# ============================================================
ADMIN_ROLES = {"ADMIN", "AUDIT_ADMIN"}
def _is_audit_admin():
    """ADMIN dan AUDIT_ADMIN memiliki akses penuh ke modul Finding."""
    return (
        current_user.is_authenticated
        and getattr(current_user, "role_code", None) in ADMIN_ROLES
    )
def _has_permission(permission_code):
    return (
        current_user.is_authenticated
        and current_user.has_permission(permission_code)
    )
def _is_finding_auditor(finding):
    """True jika user adalah auditor pada assignment execution ini."""
    execution = getattr(finding, "audit_execution", None)
    assignment = getattr(execution, "audit_assignment", None) if execution else None
    if not assignment:
        return False
    return assignment.auditor_employee_id == current_user.employee_id
def _is_finding_pic(finding):
    """True jika user adalah PIC yang ditetapkan pada Finding."""
    return (
        finding.pic_employee_id is not None
        and finding.pic_employee_id == current_user.employee_id
    )
def _can_view_finding(finding):
    if _is_audit_admin():
        return True
    if _is_finding_pic(finding):
        return True
    # User yang memiliki permission VIEW dapat melihat semua Finding,
    # tetapi hak edit tetap ditentukan terpisah.
    return _has_permission("AUDIT_FINDING_VIEW")
def _require_finding_view_access(finding):
    if not _can_view_finding(finding):
        abort(403)
def _can_edit_finding_definition(finding):
    """True jika user boleh mengubah informasi inti Finding."""
    return (
        _is_audit_admin()
        or (
            _is_finding_auditor(finding)
            and _has_permission("AUDIT_FINDING_EDIT")
        )
    )


def _require_finding_definition_access(finding):
    """Edit informasi inti Finding hanya auditor terkait/admin."""
    if _is_audit_admin():
        return
    if _is_finding_auditor(finding) and _has_permission("AUDIT_FINDING_EDIT"):
        return
    abort(403)
def _require_finding_action_access(finding):
    """Corrective action dapat dikerjakan PIC atau auditor terkait."""
    if _is_audit_admin():
        return
    if _is_finding_pic(finding):
        return
    if _is_finding_auditor(finding) and _has_permission("AUDIT_FINDING_EDIT"):
        return
    abort(403)
def _require_finding_verification_access(finding):
    """Verifikasi dan penutupan hanya oleh auditor terkait/admin."""
    if _is_audit_admin():
        return
    if _is_finding_auditor(finding) and _has_permission("AUDIT_FINDING_VERIFY"):
        return
    abort(403)
def _require_finding_delete_access(finding):
    """Penghapusan Finding hanya oleh auditor terkait/admin berizin."""
    if _is_audit_admin():
        return
    if _is_finding_auditor(finding) and _has_permission("AUDIT_FINDING_DELETE"):
        return
    abort(403)
def _require_permission_or_admin(permission_code):
    if _is_audit_admin():
        return
    if not _has_permission(permission_code):
        abort(403)
def _require_finding_belongs_to_execution(finding, execution_id):
    if finding.audit_execution_id != execution_id:
        abort(404)
def _visible_findings(findings):
    """Filter daftar agar user hanya melihat Finding yang menjadi tanggung jawabnya."""
    if _is_audit_admin():
        return findings
    return [finding for finding in findings if _can_view_finding(finding)]
# ============================================================
# Finding List
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings",
    methods=["GET"],
)
@login_required
def index(audit_id, execution_id):
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    findings = finding_service.get_by_execution(execution_id)
    findings = _visible_findings(findings)
    if not _is_audit_admin() and not _has_permission("AUDIT_FINDING_VIEW"):
        if not any(_is_finding_pic(finding) for finding in findings):
            if not (execution.audit_assignment and execution.audit_assignment.auditor_employee_id == current_user.employee_id):
                abort(403)
    return render_template(
        "audit_finding/list.html",
        audit=audit,
        execution=execution,
        findings=findings,
    )

# ============================================================
# Finding Monitoring
# ============================================================
@audit_finding_bp.route(
    "/findings/monitoring",
    methods=["GET"]
)
@login_required
def monitoring():
    """
    Centralized Finding Monitoring / Follow-up page.
    """

    findings = finding_service.get_monitoring()

    # --------------------------------------------------------
    # Permission Check
    # --------------------------------------------------------
    if (
        not _is_audit_admin()
        and not _has_permission("AUDIT_FINDING_VIEW")
        and not any(_is_finding_pic(item) for item in findings)
    ):
        abort(403)

    employees = employee_repository.get_active()

    # --------------------------------------------------------
    # Filter Parameters
    # --------------------------------------------------------
    status_filter = request.args.get("status", "").strip()
    severity_filter = request.args.get("severity", "").strip()
    pic_filter = request.args.get("pic", "").strip()
    search = request.args.get("search", "").strip()

    # --------------------------------------------------------
    # Apply Search
    # --------------------------------------------------------
    if search:
        search_lower = search.lower()

        findings = [
            finding
            for finding in findings
            if (
                search_lower in (finding.finding_no or "").lower()
                or search_lower in (finding.finding or "").lower()
            )
        ]

    # --------------------------------------------------------
    # Filter Status
    # --------------------------------------------------------
    if status_filter:
        findings = [
            finding
            for finding in findings
            if finding.status == status_filter
        ]

    # --------------------------------------------------------
    # Filter Severity
    # --------------------------------------------------------
    if severity_filter:
        findings = [
            finding
            for finding in findings
            if finding.severity == severity_filter
        ]

    # --------------------------------------------------------
    # Filter PIC
    # --------------------------------------------------------
    if pic_filter:
        try:
            pic_id = int(pic_filter)

            findings = [
                finding
                for finding in findings
                if finding.pic_employee_id == pic_id
            ]

        except ValueError:
            pass

    # --------------------------------------------------------
    # Pagination
    # Diterapkan setelah semua filter
    # --------------------------------------------------------
    page = request.args.get("page", 1, type=int)
    page = max(page, 1)

    per_page = 10

    total_findings = len(findings)

    # Minimal satu halaman agar angka 1 tetap ditampilkan
    total_pages = max(
        1,
        (total_findings + per_page - 1) // per_page
    )

    # Jika halaman yang diminta melebihi halaman terakhir
    page = min(page, total_pages)

    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    # Data yang ditampilkan hanya untuk halaman aktif
    findings_page = findings[start_index:end_index]

    # Nomor item untuk informasi "Showing ..."
    start_item = start_index + 1 if total_findings > 0 else 0
    end_item = min(end_index, total_findings)

    # --------------------------------------------------------
    # KPI
    # Tetap menghitung seluruh finding, bukan hanya halaman
    # --------------------------------------------------------
    all_findings = finding_service.get_monitoring()

    total_count = len(all_findings)

    open_count = sum(
        1
        for finding in all_findings
        if finding.status == finding_service.STATUS_OPEN
    )

    in_progress_count = sum(
        1
        for finding in all_findings
        if finding.status == finding_service.STATUS_IN_PROGRESS
    )

    verification_count = sum(
        1
        for finding in all_findings
        if finding.status
        == finding_service.STATUS_AUDITOR_VERIFICATION
    )

    closed_count = sum(
        1
        for finding in all_findings
        if finding.status == finding_service.STATUS_CLOSED
    )

    overdue_count = sum(
        1
        for finding in all_findings
        if (
            finding.target_date
            and finding.target_date < date.today()
            and finding.status != finding_service.STATUS_CLOSED
        )
    )

    # --------------------------------------------------------
    # Render Template
    # --------------------------------------------------------
    return render_template(
        "audit_finding/monitoring.html",

        # Data tabel halaman aktif
        findings=findings_page,

        # Pagination
        page=page,
        per_page=per_page,
        total_findings=total_findings,
        total_pages=total_pages,
        start_item=start_item,
        end_item=end_item,
        has_prev=page > 1,
        has_next=page < total_pages,
        prev_num=page - 1,
        next_num=page + 1,

        today=date.today(),

        # Filters
        status_filter=status_filter,
        severity_filter=severity_filter,
        pic_filter=pic_filter,
        search=search,

        # KPI
        total_count=total_count,
        open_count=open_count,
        in_progress_count=in_progress_count,
        verification_count=verification_count,
        overdue_count=overdue_count,
        closed_count=closed_count,

        # Employees
        employees=employees,
        can_edit_finding=_can_edit_finding_definition,
    )

# ============================================================
# Overdue Finding
# ============================================================
@audit_finding_bp.route(
    "/findings/overdue",
    methods=["GET"]
)
@login_required
def overdue():
    """
    Centralized Overdue Finding page.
    Displays only active findings whose target date
    has passed and whose status is not CLOSED.
    """
    findings = finding_service.get_overdue_findings()
    if (
        not _is_audit_admin()
        and not _has_permission("AUDIT_FINDING_VIEW")
        and not any(
            _is_finding_pic(item)
            for item in finding_service.get_monitoring()
        )
    ):
        abort(403)
    return render_template(
        "audit_finding/overdue.html",
        findings=findings,
        today=date.today(),
        can_edit_finding=_can_edit_finding_definition,
    )
# ============================================================
# Create Finding
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/create",
    methods=["GET", "POST"],
)
@login_required
def create(audit_id, execution_id):
    _require_permission_or_admin("AUDIT_FINDING_CREATE")
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    if not _is_audit_admin():
        assignment = execution.audit_assignment
        if (
            not assignment
            or assignment.auditor_employee_id != current_user.employee_id
            or not _has_permission("AUDIT_FINDING_CREATE")
        ):
            abort(403)
    execution_items = execution_item_repository.get_by_execution(
        execution_id
    )
    employees = employee_repository.get_active()
    if request.method == "POST":
        try:
            # =====================================================
            # FINDING DATA
            # =====================================================
            finding_source = request.form.get(
                "finding_source",
                "",
            ).strip()
            finding = request.form.get(
                "finding",
                "",
            ).strip()
            severity = request.form.get(
                "severity",
                "",
            ).strip()
            audit_execution_item_id = request.form.get(
                "audit_execution_item_id",
                type=int,
            )
            pic_employee_id = request.form.get(
                "pic_employee_id",
                type=int,
            )
            target_date = _parse_date(
                request.form.get(
                    "target_date",
                    "",
                )
            )
            corrective_action = request.form.get(
                "corrective_action",
                "",
            ).strip()
            # =====================================================
            # CREATE FINDING
            # =====================================================
            result = finding_service.create(
                audit_execution_id=execution_id,
                finding_source=finding_source,
                finding=finding,
                severity=severity,
                audit_execution_item_id=(
                    audit_execution_item_id
                ),
                pic_employee_id=pic_employee_id,
                target_date=target_date,
                corrective_action=(
                    corrective_action
                    if corrective_action
                    else None
                ),
            )
            # =====================================================
            # CHECK FINDING RESULT
            # =====================================================
            if not result.success:
                flash(
                    result.message,
                    "danger",
                )
                return render_template(
                    "audit_finding/form.html",
                    audit=audit,
                    execution=execution,
                    execution_items=execution_items,
                    employees=employees,
                    finding=None,
                    mode="create",
                )
            # Finding berhasil dibuat
            audit_finding = result.data
            # =====================================================
            # ATTACHMENT UPLOAD
            # =====================================================
            files = request.files.getlist(
                "attachments"
            )
            attachment_types = request.form.getlist(
                "attachment_types"
            )
            attachment_descriptions = request.form.getlist(
                "attachment_descriptions"
            )
            for index, file in enumerate(files):
                # Skip jika user tidak memilih file
                if not file or not file.filename:
                    continue
                # -------------------------------------------------
                # Attachment Type
                # -------------------------------------------------
                attachment_type = (
                    attachment_types[index]
                    if index < len(attachment_types)
                    else "FINDING_EVIDENCE"
                )
                # -------------------------------------------------
                # Description
                # -------------------------------------------------
                description = (
                    attachment_descriptions[index]
                    if index < len(attachment_descriptions)
                    else ""
                )
                # -------------------------------------------------
                # Upload Attachment
                # -------------------------------------------------
                attachment_result = (
                    attachment_service.create(
                        audit_finding_id=audit_finding.id,
                        file=file,
                        description=description,
                        attachment_type=attachment_type,
                    )
                )
                # -------------------------------------------------
                # Attachment failed
                # -------------------------------------------------
                if not attachment_result.success:
                    flash(
                        (
                            f"Finding created, but attachment "
                            f"'{file.filename}' failed: "
                            f"{attachment_result.message}"
                        ),
                        "warning",
                    )
            # =====================================================
            # SEND NOTIFICATION THROUGH CELERY
            # =====================================================
            if audit_finding.pic_employee_id:
                from app.tasks.notification_tasks import (
                    send_audit_finding_created_notification
                )
                send_audit_finding_created_notification.delay(
                    audit_finding.id
                )
            # =====================================================
            # SUCCESS
            # =====================================================
            flash(
                "Audit finding created successfully.",
                "success",
            )
            return redirect(
                url_for(
                    "audit_finding.index",
                    audit_id=audit_id,
                    execution_id=execution_id,
                )
            )
        except ValueError as e:
            flash(
                str(e),
                "danger",
            )
        except Exception as e:
            flash(
                f"Failed to create finding: {str(e)}",
                "danger",
            )
    return render_template(
        "audit_finding/form.html",
        audit=audit,
        execution=execution,
        execution_items=execution_items,
        employees=employees,
        finding=None,
        mode="create",
    )
# ============================================================
# Edit Finding
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(
    audit_id,
    execution_id,
    finding_id,
):
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    # =========================================================
    # Get Finding
    # =========================================================
    finding = finding_service.get_by_id(
        finding_id
    )
    if not finding:
        flash(
            "Audit finding not found.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    # =========================================================
    # Validate Finding belongs to Execution
    # =========================================================
    if finding.audit_execution_id != execution_id:
        flash(
            "Finding does not belong to this audit execution.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    _require_finding_definition_access(finding)
    # =========================================================
    # Get Form Data
    # =========================================================
    execution_items = execution_item_repository.get_by_execution(
        execution_id
    )
    employees = employee_repository.get_active()
    # =========================================================
    # POST
    # =========================================================
    if request.method == "POST":
        try:
            # =====================================================
            # FINDING DATA
            # =====================================================
            finding_source = request.form.get(
                "finding_source",
                "",
            ).strip()
            finding_text = request.form.get(
                "finding",
                "",
            ).strip()
            severity = request.form.get(
                "severity",
                "",
            ).strip()
            audit_execution_item_id = request.form.get(
                "audit_execution_item_id",
                type=int,
            )
            pic_employee_id = request.form.get(
                "pic_employee_id",
                type=int,
            )
            target_date = _parse_date(
                request.form.get(
                    "target_date",
                    "",
                )
            )
            corrective_action = request.form.get(
                "corrective_action",
                "",
            ).strip()
            # =====================================================
            # UPDATE FINDING
            # =====================================================
            result = finding_service.update(
                finding_obj=finding,
                finding_source=finding_source,
                finding=finding_text,
                severity=severity,
                audit_execution_item_id=(
                    audit_execution_item_id
                ),
                pic_employee_id=pic_employee_id,
                target_date=target_date,
                corrective_action=(
                    corrective_action
                    if corrective_action
                    else None
                ),
            )
            # =====================================================
            # CHECK UPDATE RESULT
            # =====================================================
            if not result.success:
                flash(
                    result.message,
                    "danger",
                )
                return render_template(
                    "audit_finding/form.html",
                    audit=audit,
                    execution=execution,
                    execution_items=execution_items,
                    employees=employees,
                    finding=finding,
                    mode="edit",
                )
            # =====================================================
            # ATTACHMENT UPLOAD
            # =====================================================
            files = request.files.getlist(
                "attachments"
            )
            attachment_types = request.form.getlist(
                "attachment_types"
            )
            attachment_descriptions = request.form.getlist(
                "attachment_descriptions"
            )
            attachment_success_count = 0
            attachment_failed_count = 0
            for index, file in enumerate(files):
                # -------------------------------------------------
                # Skip empty file row
                # -------------------------------------------------
                if not file or not file.filename:
                    continue
                # -------------------------------------------------
                # Attachment Type
                # -------------------------------------------------
                attachment_type = (
                    attachment_types[index]
                    if index < len(attachment_types)
                    else "FINDING_EVIDENCE"
                )
                # -------------------------------------------------
                # Description
                # -------------------------------------------------
                description = (
                    attachment_descriptions[index]
                    if index < len(attachment_descriptions)
                    else ""
                )
                # -------------------------------------------------
                # Upload
                # -------------------------------------------------
                attachment_result = (
                    attachment_service.create(
                        audit_finding_id=finding.id,
                        file=file,
                        description=description,
                        attachment_type=attachment_type,
                    )
                )
                # -------------------------------------------------
                # Upload Result
                # -------------------------------------------------
                if attachment_result.success:
                    attachment_success_count += 1
                else:
                    attachment_failed_count += 1
                    flash(
                        (
                            f"Attachment "
                            f"'{file.filename}' failed: "
                            f"{attachment_result.message}"
                        ),
                        "warning",
                    )
            # =====================================================
            # SUCCESS MESSAGE
            # =====================================================
            if attachment_success_count > 0:
                flash(
                    (
                        f"Audit finding updated successfully. "
                        f"{attachment_success_count} attachment(s) "
                        f"uploaded successfully."
                    ),
                    "success",
                )
            else:
                flash(
                    result.message,
                    "success",
                )
            # =====================================================
            # REDIRECT
            # =====================================================
            return redirect(
                url_for(
                    "audit_finding.index",
                    audit_id=audit_id,
                    execution_id=execution_id,
                )
            )
        except ValueError as e:
            flash(
                str(e),
                "danger",
            )
        except Exception as e:
            flash(
                f"Failed to update finding: {str(e)}",
                "danger",
            )
    # =========================================================
    # Render Edit Form
    # =========================================================
    attachments = attachment_service.get_by_finding(
        finding_id
    )
    return render_template(
        "audit_finding/form.html",
        audit=audit,
        execution=execution,
        execution_items=execution_items,
        employees=employees,
        finding=finding,
        attachments=attachments,
        mode="edit",
    )
# ============================================================
# Start Action
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/start",
    methods=["POST"],
)
@login_required
def start_action(
    audit_id,
    execution_id,
    finding_id,
):
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    finding = finding_service.get_by_id(
        finding_id
    )
    if not finding:
        flash(
            "Audit finding not found.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    _require_finding_belongs_to_execution(finding, execution_id)
    _require_finding_action_access(finding)
    try:
        result = finding_service.start_action(
            finding
        )
        flash(
            result.message,
            "success",
        )
    except ValueError as e:
        flash(
            str(e),
            "danger",
        )
    except Exception as e:
        flash(
            f"Failed to start finding action: {str(e)}",
            "danger",
        )
    return redirect(
        url_for(
            "audit_finding.index",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )
# ============================================================
# Complete Action
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/complete-action",
    methods=["POST"],
)
@login_required
def complete_action(
    audit_id,
    execution_id,
    finding_id,
):
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    finding = finding_service.get_by_id(
        finding_id
    )
    if not finding:
        flash(
            "Audit finding not found.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    _require_finding_belongs_to_execution(finding, execution_id)
    _require_finding_action_access(finding)
    try:
        corrective_action = request.form.get(
            "corrective_action",
            "",
        ).strip()
        action_completed_date = _parse_date(
            request.form.get(
                "action_completed_date",
                "",
            )
        )
        result = finding_service.complete_action(
            finding_obj=finding,
            corrective_action=corrective_action,
            action_completed_date=(
                action_completed_date
            ),
        )
        flash(
            result.message,
            "success",
        )
    except ValueError as e:
        flash(
            str(e),
            "danger",
        )
    except Exception as e:
        flash(
            f"Failed to complete action: {str(e)}",
            "danger",
        )
    return redirect(
        url_for(
            "audit_finding.index",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )


# ============================================================
# Corrective Action Page
# ============================================================

@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/corrective-action",
    methods=["GET", "POST"],
)
@login_required
def corrective_action(
    audit_id,
    execution_id,
    finding_id,
):
    """
    Halaman khusus untuk proses Corrective Action.

    PIC:
        - Melihat Finding yang ditugaskan kepadanya.
        - Memulai tindakan perbaikan.
        - Mengisi tindakan dan tanggal selesai.
        - Mengunggah bukti Corrective Action.
        - Mengajukan Finding untuk verifikasi.

    Auditor/Admin:
        Dapat mengakses sesuai aturan hak akses yang sudah ada.
    """

    # ---------------------------------------------------------
    # 1. Validate Audit and Execution
    # ---------------------------------------------------------
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )

    if not execution:
        return redirect(url_for("audit.index"))

    # ---------------------------------------------------------
    # 2. Get Finding
    # ---------------------------------------------------------
    finding = finding_service.get_by_id(finding_id)

    if not finding:
        flash("Audit finding not found.", "danger")

        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )

    # ---------------------------------------------------------
    # 3. Validate Finding belongs to Execution
    # ---------------------------------------------------------
    _require_finding_belongs_to_execution(
        finding,
        execution_id,
    )

    # ---------------------------------------------------------
    # 4. Validate Access
    # ---------------------------------------------------------
    _require_finding_action_access(finding)

    # ---------------------------------------------------------
    # 5. Process Form
    # ---------------------------------------------------------
    if request.method == "POST":

        action = request.form.get("action", "").strip()

        try:

            # =================================================
            # START CORRECTIVE ACTION
            # OPEN -> IN_PROGRESS
            # =================================================
            if action == "start":

                result = finding_service.start_action(
                    finding
                )

                flash(
                    result.message,
                    "success" if result.success else "danger",
                )

            # =================================================
            # COMPLETE CORRECTIVE ACTION
            # IN_PROGRESS -> ACTION_COMPLETED
            # =================================================
            elif action == "complete":

                corrective_action_text = request.form.get(
                    "corrective_action",
                    "",
                ).strip()

                action_completed_date = _parse_date(
                    request.form.get(
                        "action_completed_date",
                        "",
                    )
                )

                # ---------------------------------------------
                # Validate required input before uploading
                # ---------------------------------------------
                if not corrective_action_text:
                    raise ValueError(
                        "Corrective action is required."
                    )

                if finding.status != finding_service.STATUS_IN_PROGRESS:
                    raise ValueError(
                        "Only IN_PROGRESS findings can be completed."
                    )

                # ---------------------------------------------
                # Complete action using existing service
                # ---------------------------------------------
                result = finding_service.complete_action(
                    finding_obj=finding,
                    corrective_action=corrective_action_text,
                    action_completed_date=action_completed_date,
                )

                if result.success:

                    # -----------------------------------------
                    # Upload Corrective Action evidence
                    # -----------------------------------------
                    files = request.files.getlist("attachments")
                    descriptions = request.form.getlist(
                        "attachment_descriptions"
                    )

                    uploaded_count = 0
                    failed_count = 0

                    for index, file in enumerate(files):

                        if not file or not file.filename:
                            continue

                        description = (
                            descriptions[index].strip()
                            if index < len(descriptions)
                            else ""
                        )

                        attachment_result = attachment_service.create(
                            audit_finding_id=finding.id,
                            file=file,
                            description=description,
                            attachment_type="CORRECTIVE_ACTION",
                        )

                        if attachment_result.success:
                            uploaded_count += 1
                        else:
                            failed_count += 1

                            flash(
                                (
                                    f"Action completed, but file "
                                    f"'{file.filename}' failed to upload: "
                                    f"{attachment_result.message}"
                                ),
                                "warning",
                            )

                    flash(result.message, "success")

                    if uploaded_count:
                        flash(
                            f"{uploaded_count} corrective action evidence file(s) uploaded.",
                            "success",
                        )

                    if failed_count:
                        flash(
                            f"{failed_count} evidence file(s) failed to upload. "
                            "Please upload them again.",
                            "warning",
                        )

                else:
                    flash(result.message, "danger")

            # =================================================
            # SUBMIT FOR AUDITOR VERIFICATION
            # ACTION_COMPLETED -> AUDITOR_VERIFICATION
            # =================================================
            elif action == "submit_verification":

                result = finding_service.submit_for_verification(
                    finding
                )

                if result.success:
                    from app.tasks.notification_tasks import (
                        send_audit_finding_submitted_for_verification_notification
                    )

                    send_audit_finding_submitted_for_verification_notification.delay(
                        finding.id
                    )

                flash(
                    result.message,
                    "success" if result.success else "danger",
                )

            else:
                raise ValueError("Invalid corrective action request.")

        except ValueError as e:
            flash(str(e), "danger")

        except Exception as e:
            flash(
                f"Failed to process corrective action: {str(e)}",
                "danger",
            )

        # -----------------------------------------------------
        # 6. Return to Corrective Action Page
        # -----------------------------------------------------
        return redirect(
            url_for(
                "audit_finding.corrective_action",
                audit_id=audit_id,
                execution_id=execution_id,
                finding_id=finding_id,
            )
        )

    # ---------------------------------------------------------
    # 7. Get Corrective Action Evidence
    # ---------------------------------------------------------
    attachments = attachment_service.get_by_type(
        audit_finding_id=finding_id,
        attachment_type="CORRECTIVE_ACTION",
    )

    # ---------------------------------------------------------
    # 8. Render New Page
    # ---------------------------------------------------------
    return render_template(
        "audit_finding/corrective_action.html",
        audit=audit,
        execution=execution,
        finding=finding,
        attachments=attachments,
        can_edit_finding=_can_edit_finding_definition,
        is_finding_pic=_is_finding_pic(finding),
    )

# ============================================================
# Submit for Verification
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/submit-verification",
    methods=["POST"],
)
@login_required
def submit_verification(
    audit_id,
    execution_id,
    finding_id,
):
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    finding = finding_service.get_by_id(
        finding_id
    )
    if not finding:
        flash(
            "Audit finding not found.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    _require_finding_belongs_to_execution(finding, execution_id)
    _require_finding_action_access(finding)
    try:
        result = finding_service.submit_for_verification(
            finding
        )
        # ==========================================
        # Send Notification to Auditor
        # ==========================================
        if result.success:
            from app.tasks.notification_tasks import (
                send_audit_finding_submitted_for_verification_notification
            )
            send_audit_finding_submitted_for_verification_notification.delay(
                finding.id
            )
        flash(
            result.message,
            "success",
        )
    except ValueError as e:
        flash(
            str(e),
            "danger",
        )
    except Exception as e:
        flash(
            f"Failed to submit finding for verification: {str(e)}",
            "danger",
        )
    return redirect(
        url_for(
            "audit_finding.index",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )
# ============================================================
# Verify Finding
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/verify",
    methods=["POST"],
)
@login_required
def verify(
    audit_id,
    execution_id,
    finding_id,
):
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    finding = finding_service.get_by_id(
        finding_id
    )
    if not finding:
        flash(
            "Audit finding not found.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    _require_finding_belongs_to_execution(finding, execution_id)
    _require_finding_verification_access(finding)
    try:
        verification_status = request.form.get(
            "verification_status",
            "",
        ).strip()
        verification_result = request.form.get(
            "verification_result",
            "",
        ).strip()
        verified_by_employee_id = request.form.get(
            "verified_by_employee_id",
            type=int,
        )
        verified_date = _parse_date(
            request.form.get(
                "verified_date",
                "",
            )
        )
        result = finding_service.verify(
            finding_obj=finding,
            verification_status=verification_status,
            verification_result=verification_result,
            verified_by_employee_id=(
                verified_by_employee_id
            ),
            verified_date=verified_date,
        )
        # ==========================================
        # Send Verification Notification
        # ==========================================
        if result.success:
            from app.tasks.notification_tasks import (
                send_audit_finding_verified_notification
            )
            send_audit_finding_verified_notification.delay(
                finding.id
            )
        flash(
            result.message,
            "success",
        )
    except ValueError as e:
        flash(
            str(e),
            "danger",
        )
    except Exception as e:
        flash(
            f"Failed to verify finding: {str(e)}",
            "danger",
        )
    return redirect(
        url_for(
            "audit_finding.index",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )
# ============================================================
# Close Finding
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/close",
    methods=["POST"],
)
@login_required
def close(
    audit_id,
    execution_id,
    finding_id,
):
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    finding = finding_service.get_by_id(
        finding_id
    )
    if not finding:
        flash(
            "Audit finding not found.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    _require_finding_belongs_to_execution(finding, execution_id)
    _require_finding_verification_access(finding)
    try:
        result = finding_service.close(
            finding
        )
        flash(
            result.message,
            "success",
        )
    except ValueError as e:
        flash(
            str(e),
            "danger",
        )
    except Exception as e:
        flash(
            f"Failed to close finding: {str(e)}",
            "danger",
        )
    return redirect(
        url_for(
            "audit_finding.index",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )
# ============================================================
# Delete Finding
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/delete",
    methods=["POST"],
)
@login_required
def delete(
    audit_id,
    execution_id,
    finding_id,
):
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    finding = finding_service.get_by_id(
        finding_id
    )
    if not finding:
        flash(
            "Audit finding not found.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    if finding.audit_execution_id != execution_id:
        flash(
            "Finding does not belong to this audit execution.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    _require_finding_belongs_to_execution(finding, execution_id)
    _require_finding_delete_access(finding)
    try:
        result = finding_service.delete(
            finding
        )
        flash(
            result.message,
            "success",
        )
    except ValueError as e:
        flash(
            str(e),
            "danger",
        )
    except Exception as e:
        flash(
            f"Failed to delete finding: {str(e)}",
            "danger",
        )
    return redirect(
        url_for(
            "audit_finding.index",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )
# ============================================================
# View Attachment
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/attachments/<int:attachment_id>/view",
    methods=["GET"],
)
@login_required
def view_attachment(
    audit_id,
    execution_id,
    finding_id,
    attachment_id,
):
    """
    View image/PDF attachment in the browser.
    """
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(url_for("audit.index"))
    finding = finding_service.get_by_id(finding_id)
    if not finding:
        flash("Audit finding not found.", "danger")
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    if finding.audit_execution_id != execution_id:
        flash("Invalid audit finding.", "danger")
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    _require_finding_view_access(finding)
    attachment = attachment_service.repository.get_by_id_for_finding(
        attachment_id,
        finding_id,
    )
    if not attachment:
        flash("Attachment not found.", "danger")
        return redirect(
            url_for(
                "audit_finding.edit",
                audit_id=audit_id,
                execution_id=execution_id,
                finding_id=finding_id,
            )
        )
    allowed_view_extensions = {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
        "pdf",
    }
    extension = (attachment.file_extension or "").lower()
    if extension not in allowed_view_extensions:
        flash(
            "This file type cannot be viewed in the browser. Please download the file.",
            "warning",
        )
        return redirect(
            url_for(
                "audit_finding.edit",
                audit_id=audit_id,
                execution_id=execution_id,
                finding_id=finding_id,
            )
        )
    upload_root = attachment_service._get_upload_root()
    physical_path = upload_root / attachment.file_path
    if not physical_path.is_file():
        flash("Attachment file is missing from the server.", "danger")
        return redirect(
            url_for(
                "audit_finding.edit",
                audit_id=audit_id,
                execution_id=execution_id,
                finding_id=finding_id,
            )
        )
    return send_file(
        physical_path,
        mimetype=attachment.mime_type or None,
        as_attachment=False,
        download_name=attachment.original_filename,
    )
# ============================================================
# Download Attachment
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/attachments/<int:attachment_id>/download",
    methods=["GET"],
)
@login_required
def download_attachment(
    audit_id,
    execution_id,
    finding_id,
    attachment_id,
):
    """
    Download an attachment.
    """
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(url_for("audit.index"))
    finding = finding_service.get_by_id(finding_id)
    if not finding:
        flash("Audit finding not found.", "danger")
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    if finding.audit_execution_id != execution_id:
        flash("Invalid audit finding.", "danger")
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    _require_finding_view_access(finding)
    attachment = attachment_service.repository.get_by_id_for_finding(
        attachment_id,
        finding_id,
    )
    if not attachment:
        flash("Attachment not found.", "danger")
        return redirect(
            url_for(
                "audit_finding.edit",
                audit_id=audit_id,
                execution_id=execution_id,
                finding_id=finding_id,
            )
        )
    upload_root = attachment_service._get_upload_root()
    physical_path = upload_root / attachment.file_path
    if not physical_path.is_file():
        flash("Attachment file is missing from the server.", "danger")
        return redirect(
            url_for(
                "audit_finding.edit",
                audit_id=audit_id,
                execution_id=execution_id,
                finding_id=finding_id,
            )
        )
    return send_file(
        physical_path,
        mimetype=attachment.mime_type or None,
        as_attachment=True,
        download_name=attachment.original_filename,
    )
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>/attachments/<int:attachment_id>/delete",
    methods=["POST"],
)
@login_required
def delete_attachment(
    audit_id,
    execution_id,
    finding_id,
    attachment_id,
):
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for("audit.index")
        )
    # =========================================================
    # Validate Finding
    # =========================================================
    finding = finding_service.get_by_id(
        finding_id
    )
    if not finding:
        flash(
            "Audit finding not found.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    # =========================================================
    # Make sure finding belongs to this execution
    # =========================================================
    if finding.audit_execution_id != execution_id:
        flash(
            "Invalid audit finding.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    # =========================================================
    # Delete Attachment
    # =========================================================
    _require_finding_belongs_to_execution(finding, execution_id)
    _require_finding_action_access(finding)
    result = attachment_service.delete(
        attachment_id=attachment_id,
        audit_finding_id=finding_id,
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
    # =========================================================
    # Back to Finding
    # =========================================================
    return redirect(
        url_for(
            "audit_finding.index",
            audit_id=audit_id,
            execution_id=execution_id,
        )
    )
# ============================================================
# Finding Detail
# ============================================================
@audit_finding_bp.route(
    "/<int:audit_id>/executions/<int:execution_id>/findings/<int:finding_id>",
    methods=["GET"],
)
@login_required
def detail(
    audit_id,
    execution_id,
    finding_id,
):
    # =========================================================
    # Validate Audit & Execution
    # =========================================================
    audit, execution = _get_audit_and_execution(
        audit_id,
        execution_id,
    )
    if not execution:
        return redirect(
            url_for(
                "audit.index"
            )
        )
    # =========================================================
    # Get Finding
    # =========================================================
    finding = finding_service.get_by_id(
        finding_id
    )
    if not finding:
        flash(
            "Audit finding not found.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    # =========================================================
    # Validate Finding belongs to Execution
    # =========================================================
    if finding.audit_execution_id != execution_id:
        flash(
            "Finding does not belong to this audit execution.",
            "danger",
        )
        return redirect(
            url_for(
                "audit_finding.index",
                audit_id=audit_id,
                execution_id=execution_id,
            )
        )
    # =========================================================
    # Get Attachments
    # =========================================================
    _require_finding_view_access(finding)
    attachments = attachment_service.get_by_finding(
        finding_id
    )
    # =========================================================
    # Render Detail
    # =========================================================
    return render_template(
        "audit_finding/detail.html",
        audit=audit,
        execution=execution,
        finding=finding,
        attachments=attachments,
        can_edit_finding=_can_edit_finding_definition,
    )
