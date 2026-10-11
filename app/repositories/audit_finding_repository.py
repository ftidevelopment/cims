from app.models.audit_finding import AuditFinding
from app.repositories.base_repository import BaseRepository


class AuditFindingRepository(BaseRepository):
    model = AuditFinding

    searchable_fields = [
        AuditFinding.finding_no,
        AuditFinding.finding,
        AuditFinding.severity,
        AuditFinding.status,
        AuditFinding.finding_source,
        AuditFinding.corrective_action,
        AuditFinding.verification_result,
    ]

    sortable_fields = {
        "finding_no": AuditFinding.finding_no,
        "finding_source": AuditFinding.finding_source,
        "severity": AuditFinding.severity,
        "status": AuditFinding.status,
        "target_date": AuditFinding.target_date,
        "action_completed_date": AuditFinding.action_completed_date,
        "verified_date": AuditFinding.verified_date,
        "created_at": AuditFinding.created_at,
    }

    def __init__(self):
        super().__init__(AuditFinding)

    # ============================================================
    # Get Findings by Audit Execution
    # ============================================================

    def get_by_execution(self, audit_execution_id: int):
        """
        Get all active findings for a specific audit execution.
        """
        return (
            self.model.query
            .filter_by(
                audit_execution_id=audit_execution_id,
                is_active=True
            )
            .order_by(
                self.model.created_at.asc()
            )
            .all()
        )

    # ============================================================
    # Get Findings by Execution Item
    # ============================================================

    def get_by_execution_item(self, audit_execution_item_id: int):
        """
        Get all active findings related to a specific
        audit execution checklist item.
        """
        return (
            self.model.query
            .filter_by(
                audit_execution_item_id=audit_execution_item_id,
                is_active=True
            )
            .order_by(
                self.model.created_at.asc()
            )
            .all()
        )

    # ============================================================
    # Get Findings by PIC
    # ============================================================

    def get_by_pic(self, pic_employee_id: int):
        """
        Get all active findings assigned to a specific PIC.
        """
        return (
            self.model.query
            .filter_by(
                pic_employee_id=pic_employee_id,
                is_active=True
            )
            .order_by(
                self.model.target_date.asc(),
                self.model.created_at.desc()
            )
            .all()
        )

    # ============================================================
    # Get Findings by Status
    # ============================================================

    def get_by_status(self, status: str):
        """
        Get all active findings with a specific status.
        """
        return (
            self.model.query
            .filter_by(
                status=status,
                is_active=True
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ============================================================
    # Get Findings by Severity
    # ============================================================

    def get_by_severity(self, severity: str):
        """
        Get all active findings with a specific severity.
        """
        return (
            self.model.query
            .filter_by(
                severity=severity,
                is_active=True
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ============================================================
    # Get Findings by Source
    # ============================================================

    def get_by_source(self, finding_source: str):
        """
        Get all active findings from a specific source.

        Source:
        - CHECKLIST
        - OUTSIDE_CHECKLIST
        """
        return (
            self.model.query
            .filter_by(
                finding_source=finding_source,
                is_active=True
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ============================================================
    # Get Finding by Number
    # ============================================================

    def get_by_finding_no(self, finding_no: str):
        """
        Get an active finding by finding number.
        """
        return (
            self.model.query
            .filter_by(
                finding_no=finding_no,
                is_active=True
            )
            .first()
        )

    # ============================================================
    # Check Finding Number
    # ============================================================

    def exists_by_finding_no(self, finding_no: str):
        """
        Check whether an active finding number already exists.
        """
        return self.get_by_finding_no(finding_no) is not None

    # ============================================================
    # Get Finding by Execution and Item
    # ============================================================

    def get_by_execution_and_item(
        self,
        audit_execution_id: int,
        audit_execution_item_id: int
    ):
        """
        Get an active finding related to a specific
        execution and checklist item.
        """
        return (
            self.model.query
            .filter_by(
                audit_execution_id=audit_execution_id,
                audit_execution_item_id=audit_execution_item_id,
                is_active=True
            )
            .order_by(
                self.model.created_at.asc()
            )
            .all()
        )

    # ============================================================
    # Get Open Findings
    # ============================================================

    def get_open_findings(self):
        """
        Get all active findings that are not closed.

        Useful for dashboard / monitoring.
        """
        return (
            self.model.query
            .filter(
                self.model.is_active.is_(True),
                self.model.status != "CLOSED"
            )
            .order_by(
                self.model.target_date.asc(),
                self.model.created_at.desc()
            )
            .all()
        )

    # ============================================================
    # Get Findings for Verification
    # ============================================================

    def get_for_verification(self):
        """
        Get findings waiting for auditor verification.
        """
        return (
            self.model.query
            .filter_by(
                status="AUDITOR_VERIFICATION",
                is_active=True
            )
            .order_by(
                self.model.action_completed_date.asc(),
                self.model.created_at.asc()
            )
            .all()
        )

    # ============================================================
    # Count by Status
    # ============================================================

    def count_by_status(self, status: str) -> int:
        """
        Count active findings by status.
        """
        return (
            self.model.query
            .filter_by(
                status=status,
                is_active=True
            )
            .count()
        )

    # ============================================================
    # Count by Severity
    # ============================================================

    def count_by_severity(self, severity: str) -> int:
        """
        Count active findings by severity.
        """
        return (
            self.model.query
            .filter_by(
                severity=severity,
                is_active=True
            )
            .count()
        )

    # ============================================================
    # Count by Execution
    # ============================================================

    def count_by_execution(self, audit_execution_id: int) -> int:
        """
        Count active findings for an audit execution.
        """
        return (
            self.model.query
            .filter_by(
                audit_execution_id=audit_execution_id,
                is_active=True
            )
            .count()
        )

        # ============================================================
    # Get All Findings for Monitoring
    # ============================================================

    def get_all_monitoring(self):
        """
        Get all active findings for centralized monitoring.

        Used by Finding Monitoring / Follow-up page.
        Findings are ordered by:
        1. Non-closed findings first
        2. Target date ascending
        3. Created date descending
        """
        return (
            self.model.query
            .filter(
                self.model.is_active.is_(True)
            )
            .order_by(
                self.model.status.asc(),
                self.model.target_date.asc(),
                self.model.created_at.desc()
            )
            .all()
        )

        # ============================================================
    # Get Overdue Findings
    # ============================================================

    def get_overdue_findings(self, today):
        """
        Get all active findings that are overdue.

        Overdue condition:
        - target_date is not NULL
        - target_date is before today
        - status is not CLOSED

        Results are ordered by:
        1. Oldest target date first
        2. Severity
        3. Created date descending
        """
        return (
            self.model.query
            .filter(
                self.model.is_active.is_(True),
                self.model.target_date.isnot(None),
                self.model.target_date < today,
                self.model.status != "CLOSED",
            )
            .order_by(
                self.model.target_date.asc(),
                self.model.severity.asc(),
                self.model.created_at.desc(),
            )
            .all()
        )