from app.models.audit_execution import AuditExecution
from app.repositories.base_repository import BaseRepository


class AuditExecutionRepository(BaseRepository):
    """
    Repository untuk Audit Execution.
    """

    model = AuditExecution

    searchable_fields = [
        AuditExecution.status,
        AuditExecution.remark,
    ]

    sortable_fields = {
        "execution_date": AuditExecution.execution_date,
        "status": AuditExecution.status,
        "started_at": AuditExecution.started_at,
        "completed_at": AuditExecution.completed_at,
        "created_at": AuditExecution.created_at,
    }

    def __init__(self):
        super().__init__(AuditExecution)

    # ======================================================
    # GET BY ASSIGNMENT
    # ======================================================

    def get_by_assignment(
        self,
        audit_assignment_id: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_assignment_id=audit_assignment_id,
                is_active=True,
            )
            .order_by(
                self.model.execution_date.desc(),
                self.model.created_at.desc(),
            )
            .all()
        )

    # ======================================================
    # GET BY CHECKLIST
    # ======================================================

    def get_by_checklist(
        self,
        audit_checklist_id: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_checklist_id=audit_checklist_id,
                is_active=True,
            )
            .order_by(
                self.model.execution_date.desc(),
                self.model.created_at.desc(),
            )
            .all()
        )

    # ======================================================
    # GET BY STATUS
    # ======================================================

    def get_by_status(
        self,
        status: str,
    ):
        return (
            self.model.query
            .filter_by(
                status=status,
                is_active=True,
            )
            .order_by(
                self.model.execution_date.desc(),
                self.model.created_at.desc(),
            )
            .all()
        )

    # ======================================================
    # GET BY ASSIGNMENT + STATUS
    # ======================================================

    def get_by_assignment_and_status(
        self,
        audit_assignment_id: int,
        status: str,
    ):
        return (
            self.model.query
            .filter_by(
                audit_assignment_id=audit_assignment_id,
                status=status,
                is_active=True,
            )
            .order_by(
                self.model.execution_date.desc(),
                self.model.created_at.desc(),
            )
            .all()
        )

    # ======================================================
    # GET LATEST EXECUTION
    # ======================================================

    def get_latest_by_assignment(
        self,
        audit_assignment_id: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_assignment_id=audit_assignment_id,
                is_active=True,
            )
            .order_by(
                self.model.execution_date.desc(),
                self.model.created_at.desc(),
            )
            .first()
        )

    # ======================================================
    # GET EXISTING EXECUTION
    # ======================================================

    def get_existing_execution(
        self,
        audit_assignment_id: int,
        audit_checklist_id: int,
        execution_date,
    ):
        return (
            self.model.query
            .filter_by(
                audit_assignment_id=audit_assignment_id,
                audit_checklist_id=audit_checklist_id,
                execution_date=execution_date,
                is_active=True,
            )
            .first()
        )

    # ======================================================
    # EXISTS EXECUTION
    # ======================================================

    def exists_execution(
        self,
        audit_assignment_id: int,
        audit_checklist_id: int,
        execution_date,
    ) -> bool:
        return (
            self.get_existing_execution(
                audit_assignment_id=audit_assignment_id,
                audit_checklist_id=audit_checklist_id,
                execution_date=execution_date,
            )
            is not None
        )