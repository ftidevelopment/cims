from datetime import date

from app.extensions import db
from app.models.audit_finding import AuditFinding
from app.repositories.audit_finding_repository import AuditFindingRepository
from app.repositories.audit_execution_repository import AuditExecutionRepository
from app.repositories.audit_execution_item_repository import AuditExecutionItemRepository
from app.repositories.employee_repository import EmployeeRepository
from app.services.base_service import BaseService
from app.core.service_result import ServiceResult
from app.core.transaction_manager import TransactionManager


class AuditFindingService(BaseService):
    """
    Service untuk mengelola Audit Finding.

    Finding dapat berasal dari:
    - CHECKLIST
    - OUTSIDE_CHECKLIST

    Status:
    - OPEN
    - IN_PROGRESS
    - ACTION_COMPLETED
    - AUDITOR_VERIFICATION
    - PASS
    - CLOSED

    Verification:
    - PASS
    - FAIL
    """

    FINDING_SOURCE_CHECKLIST = "CHECKLIST"
    FINDING_SOURCE_OUTSIDE_CHECKLIST = "OUTSIDE_CHECKLIST"

    VALID_SOURCES = [
        FINDING_SOURCE_CHECKLIST,
        FINDING_SOURCE_OUTSIDE_CHECKLIST,
    ]

    SEVERITY_CRITICAL = "CRITICAL"
    SEVERITY_MAJOR = "MAJOR"
    SEVERITY_MINOR = "MINOR"
    SEVERITY_OBSERVATION = "OBSERVATION"

    VALID_SEVERITIES = [
        SEVERITY_CRITICAL,
        SEVERITY_MAJOR,
        SEVERITY_MINOR,
        SEVERITY_OBSERVATION,
    ]

    STATUS_OPEN = "OPEN"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_ACTION_COMPLETED = "ACTION_COMPLETED"
    STATUS_AUDITOR_VERIFICATION = "AUDITOR_VERIFICATION"
    STATUS_PASS = "PASS"
    STATUS_CLOSED = "CLOSED"

    VALID_STATUSES = [
        STATUS_OPEN,
        STATUS_IN_PROGRESS,
        STATUS_ACTION_COMPLETED,
        STATUS_AUDITOR_VERIFICATION,
        STATUS_PASS,
        STATUS_CLOSED,
    ]

    VERIFICATION_PASS = "PASS"
    VERIFICATION_FAIL = "FAIL"

    VALID_VERIFICATION_STATUS = [
        VERIFICATION_PASS,
        VERIFICATION_FAIL,
    ]

    def __init__(
        self,
        repository=None,
        execution_repository=None,
        execution_item_repository=None,
        employee_repository=None,
    ):
        super().__init__()

        self.repository = (
            repository
            if repository is not None
            else AuditFindingRepository()
        )

        self.execution_repository = (
            execution_repository
            if execution_repository is not None
            else AuditExecutionRepository()
        )

        self.execution_item_repository = (
            execution_item_repository
            if execution_item_repository is not None
            else AuditExecutionItemRepository()
        )

        self.employee_repository = (
            employee_repository
            if employee_repository is not None
            else EmployeeRepository()
        )

    # ============================================================
    # Finding Number
    # ============================================================

    def generate_finding_no(self):
        """
        Generate finding number automatically.

        Format:
        AF20260001
        AF20260002
        AF20260003
        """

        year = date.today().year
        prefix = f"AF{year}"

        last_finding = (
            AuditFinding.query
            .filter(
                AuditFinding.finding_no.like(f"{prefix}%")
            )
            .order_by(
                AuditFinding.finding_no.desc()
            )
            .first()
        )

        if not last_finding:
            sequence = 1
        else:
            try:
                last_sequence = int(
                    last_finding.finding_no[-4:]
                )
                sequence = last_sequence + 1
            except (ValueError, TypeError):
                sequence = 1

        return f"{prefix}{sequence:04d}"

    # ============================================================
    # Validation
    # ============================================================

    def _validate_source(
        self,
        finding_source,
        audit_execution_item_id=None,
    ):
        """
        Validate finding source.

        CHECKLIST:
            audit_execution_item_id wajib ada.

        OUTSIDE_CHECKLIST:
            audit_execution_item_id harus NULL.
        """

        if finding_source not in self.VALID_SOURCES:
            raise ValueError(
                "Invalid finding source. "
                "Allowed values: CHECKLIST or OUTSIDE_CHECKLIST."
            )

        if (
            finding_source == self.FINDING_SOURCE_CHECKLIST
            and not audit_execution_item_id
        ):
            raise ValueError(
                "Audit execution checklist item is required "
                "for CHECKLIST finding."
            )

        if (
            finding_source == self.FINDING_SOURCE_OUTSIDE_CHECKLIST
            and audit_execution_item_id
        ):
            raise ValueError(
                "Audit execution checklist item must be empty "
                "for OUTSIDE_CHECKLIST finding."
            )

    def _validate_severity(self, severity):
        if severity not in self.VALID_SEVERITIES:
            raise ValueError(
                "Invalid severity. "
                "Allowed values: CRITICAL, MAJOR, MINOR, OBSERVATION."
            )

    def _validate_status(self, status):
        if status not in self.VALID_STATUSES:
            raise ValueError(
                "Invalid finding status."
            )

    def _validate_verification_status(self, verification_status):
        if (
            verification_status is not None
            and verification_status not in self.VALID_VERIFICATION_STATUS
        ):
            raise ValueError(
                "Invalid verification status. "
                "Allowed values: PASS or FAIL."
            )

    # ============================================================
    # Validate Audit Execution
    # ============================================================

    def _get_execution(self, audit_execution_id):
        execution = self.execution_repository.get_by_id(
            audit_execution_id
        )

        if not execution:
            raise ValueError(
                "Audit execution not found."
            )

        if not execution.is_active:
            raise ValueError(
                "Audit execution is inactive."
            )

        return execution

    # ============================================================
    # Validate Execution Item
    # ============================================================

    def _get_execution_item(
        self,
        audit_execution_item_id,
        audit_execution_id,
    ):
        item = self.execution_item_repository.get_by_id(
            audit_execution_item_id
        )

        if not item:
            raise ValueError(
                "Audit execution checklist item not found."
            )

        if not item.is_active:
            raise ValueError(
                "Audit execution checklist item is inactive."
            )

        if item.audit_execution_id != audit_execution_id:
            raise ValueError(
                "Checklist item does not belong to "
                "the selected audit execution."
            )

        return item

    # ============================================================
    # Validate PIC
    # ============================================================

    def _validate_pic(self, pic_employee_id):
        if not pic_employee_id:
            return None

        employee = self.employee_repository.get_by_id(
            pic_employee_id
        )

        if not employee:
            raise ValueError(
                "PIC employee not found."
            )

        if not employee.is_active:
            raise ValueError(
                "PIC employee is inactive."
            )

        return employee

    # ============================================================
    # Create
    # ============================================================

    def create(
        self,
        audit_execution_id,
        finding_source,
        finding,
        severity,
        audit_execution_item_id=None,
        pic_employee_id=None,
        target_date=None,
        corrective_action=None,
    ):
        """
        Create a new audit finding.
        """

        if not finding or not finding.strip():
            raise ValueError(
                "Finding is required."
            )

        self._validate_source(
            finding_source,
            audit_execution_item_id,
        )

        self._validate_severity(severity)

        execution = self._get_execution(
            audit_execution_id
        )

        if audit_execution_item_id:
            self._get_execution_item(
                audit_execution_item_id,
                audit_execution_id,
            )

        if pic_employee_id:
            self._validate_pic(
                pic_employee_id
            )

        finding_no = self.generate_finding_no()

        finding_obj = AuditFinding(
            finding_no=finding_no,
            audit_execution_id=audit_execution_id,
            audit_execution_item_id=audit_execution_item_id,
            finding_source=finding_source,
            finding=finding.strip(),
            severity=severity,
            pic_employee_id=pic_employee_id,
            target_date=target_date,
            status=self.STATUS_OPEN,
            corrective_action=corrective_action,
        )

        try:
            with TransactionManager():
                self.repository.create(
                    finding_obj
                )

            return ServiceResult(
                success=True,
                message="Audit finding created successfully.",
                data=finding_obj
            )

        except Exception as e:
            raise e

    # ============================================================
    # Update
    # ============================================================

    def update(
        self,
        finding_obj,
        finding_source,
        finding,
        severity,
        audit_execution_item_id=None,
        pic_employee_id=None,
        target_date=None,
        corrective_action=None,
    ):
        """
        Update finding information.
        """

        if not finding_obj:
            raise ValueError(
                "Audit finding not found."
            )

        if not finding:
            raise ValueError(
                "Finding is required."
            )

        self._validate_source(
            finding_source,
            audit_execution_item_id,
        )

        self._validate_severity(severity)

        self._get_execution(
            finding_obj.audit_execution_id
        )

        if audit_execution_item_id:
            self._get_execution_item(
                audit_execution_item_id,
                finding_obj.audit_execution_id,
            )

        if pic_employee_id:
            self._validate_pic(
                pic_employee_id
            )

        finding_obj.finding_source = finding_source
        finding_obj.audit_execution_item_id = (
            audit_execution_item_id
        )
        finding_obj.finding = finding.strip()
        finding_obj.severity = severity
        finding_obj.pic_employee_id = pic_employee_id
        finding_obj.target_date = target_date
        finding_obj.corrective_action = corrective_action

        try:
            with TransactionManager():
                db.session.flush()

            return ServiceResult(
                success=True,
                message="Audit finding updated successfully.",
                data=finding_obj
            )

        except Exception as e:
            raise e

    # ============================================================
    # Start Action
    # ============================================================

    def start_action(self, finding_obj):
        """
        Change finding status:

        OPEN -> IN_PROGRESS
        """

        if not finding_obj:
            raise ValueError(
                "Audit finding not found."
            )

        if finding_obj.status != self.STATUS_OPEN:
            raise ValueError(
                "Only OPEN findings can be started."
            )

        finding_obj.status = self.STATUS_IN_PROGRESS

        try:
            with TransactionManager():
                db.session.flush()

            return ServiceResult(
                success=True,
                message="Finding action started successfully.",
                data=finding_obj
            )

        except Exception as e:
            raise e

    # ============================================================
    # Complete Action
    # ============================================================

    def complete_action(
        self,
        finding_obj,
        corrective_action,
        action_completed_date=None,
    ):
        """
        Change finding status:

        IN_PROGRESS -> ACTION_COMPLETED
        """

        if not finding_obj:
            raise ValueError(
                "Audit finding not found."
            )

        if finding_obj.status != self.STATUS_IN_PROGRESS:
            raise ValueError(
                "Only IN_PROGRESS findings can be completed."
            )

        if (
            not corrective_action
            or not corrective_action.strip()
        ):
            raise ValueError(
                "Corrective action is required."
            )

        finding_obj.corrective_action = (
            corrective_action.strip()
        )

        finding_obj.action_completed_date = (
            action_completed_date
            if action_completed_date
            else date.today()
        )

        finding_obj.status = (
            self.STATUS_ACTION_COMPLETED
        )

        try:
            with TransactionManager():
                db.session.flush()

            return ServiceResult(
                success=True,
                message="Corrective action completed successfully.",
                data=finding_obj
            )

        except Exception as e:
            raise e

    # ============================================================
    # Submit for Verification
    # ============================================================

    def submit_for_verification(self, finding_obj):
        """
        Change finding status:

        ACTION_COMPLETED -> AUDITOR_VERIFICATION
        """

        if not finding_obj:
            raise ValueError(
                "Audit finding not found."
            )

        if finding_obj.status != self.STATUS_ACTION_COMPLETED:
            raise ValueError(
                "Only ACTION_COMPLETED findings "
                "can be submitted for verification."
            )

        finding_obj.status = (
            self.STATUS_AUDITOR_VERIFICATION
        )

        try:
            with TransactionManager():
                db.session.flush()

            return ServiceResult(
                success=True,
                message="Finding submitted for auditor verification.",
                data=finding_obj
            )

        except Exception as e:
            raise e

    # ============================================================
    # Verify Finding
    # ============================================================

    def verify(
        self,
        finding_obj,
        verification_status,
        verification_result,
        verified_by_employee_id,
        verified_date=None,
    ):
        """
        Verify finding.

        PASS:
            AUDITOR_VERIFICATION -> PASS

        FAIL:
            AUDITOR_VERIFICATION -> IN_PROGRESS
        """

        if not finding_obj:
            raise ValueError(
                "Audit finding not found."
            )

        if finding_obj.status != self.STATUS_AUDITOR_VERIFICATION:
            raise ValueError(
                "Only findings in AUDITOR_VERIFICATION "
                "can be verified."
            )

        self._validate_verification_status(
            verification_status
        )

        if (
            not verification_result
            or not verification_result.strip()
        ):
            raise ValueError(
                "Verification result is required."
            )

        self._validate_pic(
            verified_by_employee_id
        )

        finding_obj.verification_result = (
            verification_result.strip()
        )

        finding_obj.verification_status = (
            verification_status
        )

        finding_obj.verified_by_employee_id = (
            verified_by_employee_id
        )

        finding_obj.verified_date = (
            verified_date
            if verified_date
            else date.today()
        )

        if verification_status == self.VERIFICATION_PASS:
            finding_obj.status = self.STATUS_PASS
        else:
            finding_obj.status = self.STATUS_IN_PROGRESS

        try:
            with TransactionManager():
                db.session.flush()

            if verification_status == self.VERIFICATION_PASS:
                message = (
                    "Finding verification passed successfully."
                )
            else:
                message = (
                    "Finding verification failed. "
                    "Finding returned to IN_PROGRESS."
                )

            return ServiceResult(
                success=True,
                message=message,
                data=finding_obj
            )

        except Exception as e:
            raise e

    # ============================================================
    # Close Finding
    # ============================================================

    def close(self, finding_obj):
        """
        Close a finding after verification PASS.

        PASS -> CLOSED
        """

        if not finding_obj:
            raise ValueError(
                "Audit finding not found."
            )

        if finding_obj.status != self.STATUS_PASS:
            raise ValueError(
                "Only PASS findings can be closed."
            )

        finding_obj.status = self.STATUS_CLOSED

        try:
            with TransactionManager():
                db.session.flush()

            return ServiceResult(
                success=True,
                message="Audit finding closed successfully.",
                data=finding_obj
            )

        except Exception as e:
            raise e

    # ============================================================
    # Delete
    # ============================================================

    def delete(self, finding_obj):
        """
        Soft delete audit finding.
        """

        if not finding_obj:
            raise ValueError(
                "Audit finding not found."
            )

        try:
            with TransactionManager():
                finding_obj.is_active = False

                db.session.flush()

            return ServiceResult(
                success=True,
                message="Audit finding deleted successfully.",
                data=finding_obj
            )

        except Exception as e:
            raise e

    # ============================================================
    # Restore
    # ============================================================

    def restore(self, finding_obj):
        """
        Restore inactive audit finding.
        """

        if not finding_obj:
            raise ValueError(
                "Audit finding not found."
            )

        try:
            with TransactionManager():
                finding_obj.is_active = True

                db.session.flush()

            return ServiceResult(
                success=True,
                message="Audit finding restored successfully.",
                data=finding_obj
            )

        except Exception as e:
            raise e

    # ============================================================
    # Get Findings by Execution
    # ============================================================

    def get_by_execution(self, audit_execution_id):
        return self.repository.get_by_execution(
            audit_execution_id
        )

    # ============================================================
    # Get Finding by ID
    # ============================================================

    def get_by_id(self, finding_id):
        return self.repository.get_by_id(
            finding_id
        )

    # ============================================================
    # Get Finding by Number
    # ============================================================

    def get_by_finding_no(self, finding_no):
        return self.repository.get_by_finding_no(
            finding_no
        )

    # ============================================================
    # Get Open Findings
    # ============================================================

    def get_open_findings(self):
        return self.repository.get_open_findings()

    # ============================================================
    # Get Findings for Verification
    # ============================================================

    def get_for_verification(self):
        return self.repository.get_for_verification()

        # ============================================================
    # Get Overdue Findings
    # ============================================================

    def get_overdue_findings(self):
        """
        Get all active findings that are overdue.

        Overdue condition:
        - target_date is not NULL
        - target_date is before today
        - status is not CLOSED
        """
        return self.repository.get_overdue_findings(
            date.today()
        )

        # ============================================================
    # Get Findings for Monitoring
    # ============================================================

    def get_monitoring(self):
        """
        Get all active findings for centralized monitoring.

        Used by Finding Monitoring / Follow-up page.
        """
        return self.repository.get_all_monitoring()