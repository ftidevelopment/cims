from datetime import datetime, date

from app.services.base_service import BaseService
from app.core.service_result import ServiceResult
from app.core.transaction_manager import TransactionManager

from app.repositories.audit_execution_repository import AuditExecutionRepository
from app.repositories.audit_execution_item_repository import AuditExecutionItemRepository

from app.models.audit_assignment import AuditAssignment
from app.models.audit_checklist import AuditChecklist
from app.models.audit_execution import AuditExecution
from app.models.audit_execution_item import AuditExecutionItem


class AuditExecutionService(BaseService):

    def __init__(self):
        self.repository = AuditExecutionRepository()
        self.item_repository = AuditExecutionItemRepository()
        self.transaction = TransactionManager()

    # =========================================================
    # GET
    # =========================================================

    def get_by_id(self, execution_id):
        return self.repository.get_by_id(execution_id)

    def get_by_assignment(self, audit_assignment_id):
        return self.repository.get_by_assignment(audit_assignment_id)

    def get_by_checklist(self, audit_checklist_id):
        return self.repository.get_by_checklist(audit_checklist_id)

    def get_by_status(self, status):
        return self.repository.get_by_status(status)

    def get_latest_by_assignment(self, audit_assignment_id):
        return self.repository.get_latest_by_assignment(audit_assignment_id)

    # =========================================================
    # CREATE
    # =========================================================

    def create(
        self,
        audit_assignment_id,
        audit_checklist_id,
        execution_date=None,
        remark=None
    ):
        try:
            # -------------------------------------------------
            # Validate Assignment
            # -------------------------------------------------
            assignment = AuditAssignment.query.filter_by(
                id=audit_assignment_id,
                is_active=True
            ).first()

            if not assignment:
                raise ValueError("Audit Assignment not found.")

            # -------------------------------------------------
            # Validate Checklist
            # -------------------------------------------------
            checklist = AuditChecklist.query.filter_by(
                id=audit_checklist_id,
                is_active=True
            ).first()

            if not checklist:
                raise ValueError("Audit Checklist not found.")

            # -------------------------------------------------
            # Execution Date
            # -------------------------------------------------
            if not execution_date:
                execution_date = date.today()

            # -------------------------------------------------
            # Prevent Duplicate Execution
            # -------------------------------------------------
            existing = self.repository.get_existing_execution(
                audit_assignment_id=audit_assignment_id,
                audit_checklist_id=audit_checklist_id,
                execution_date=execution_date
            )

            if existing:
                raise ValueError(
                    "Audit Execution already exists for this assignment, "
                    "checklist, and execution date."
                )

            # -------------------------------------------------
            # Create Execution
            # -------------------------------------------------
            execution = AuditExecution()

            execution.audit_assignment_id = audit_assignment_id
            execution.audit_checklist_id = audit_checklist_id
            execution.execution_date = execution_date
            execution.status = "NOT_STARTED"
            execution.remark = remark

            self.repository.create(
                execution
            )

            self.transaction.commit()

            # -------------------------------------------------
            # Create Snapshot of Checklist Items
            # -------------------------------------------------
            checklist_items = [
                item for item in checklist.items
                if item.is_active
            ]

            for checklist_item in checklist_items:

                execution_item = AuditExecutionItem()

                execution_item.audit_execution_id = execution.id
                execution_item.audit_checklist_item_id = checklist_item.id
                execution_item.item_no = checklist_item.item_no
                execution_item.question = checklist_item.question
                execution_item.result = None
                execution_item.remark = None

                self.item_repository.create(
                    execution_item
                )

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Audit Execution created successfully.",
                data=execution
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to create Audit Execution: {ex}"
            )

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        execution_id,
        execution_date=None,
        status=None,
        remark=None
    ):
        try:
            execution = self.repository.get_by_id(execution_id)

            if not execution:
                return ServiceResult(
                    success=False,
                    message="Audit Execution not found."
                )

            if execution_date:
                execution.execution_date = execution_date

            if status:
                valid_statuses = [
                    "NOT_STARTED",
                    "IN_PROGRESS",
                    "COMPLETED"
                ]

                if status not in valid_statuses:
                    raise ValueError(
                        f"Invalid execution status: {status}"
                    )

                execution.status = status

            if remark is not None:
                execution.remark = remark

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Audit Execution updated successfully.",
                data=execution
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to update Audit Execution: {ex}"
            )

    # =========================================================
    # START EXECUTION
    # =========================================================

    def start(self, execution_id):
        try:
            execution = self.repository.get_by_id(execution_id)

            if not execution:
                return ServiceResult(
                    success=False,
                    message="Audit Execution not found."
                )

            if execution.status == "COMPLETED":
                return ServiceResult(
                    success=False,
                    message="Audit Execution is already completed."
                )

            execution.status = "IN_PROGRESS"

            if not execution.started_at:
                execution.started_at = datetime.utcnow()

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Audit Execution started successfully.",
                data=execution
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to start Audit Execution: {ex}"
            )

    # =========================================================
    # COMPLETE EXECUTION
    # =========================================================

    def complete(self, execution_id):
        try:
            execution = self.repository.get_by_id(execution_id)

            if not execution:
                return ServiceResult(
                    success=False,
                    message="Audit Execution not found."
                )

            items = self.item_repository.get_by_execution(
                execution_id
            )

            if not items:
                raise ValueError(
                    "Audit Execution has no checklist items."
                )

            # Semua item wajib memiliki result
            incomplete_items = [
                item for item in items
                if not item.result
            ]

            if incomplete_items:
                raise ValueError(
                    f"There are {len(incomplete_items)} "
                    "checklist items without result."
                )

            execution.status = "COMPLETED"
            execution.completed_at = datetime.utcnow()

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Audit Execution completed successfully.",
                data=execution
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to complete Audit Execution: {ex}"
            )

    # =========================================================
    # DELETE
    # =========================================================

    def delete(self, execution_id):
        try:
            execution = self.repository.get_by_id(execution_id)

            if not execution:
                return ServiceResult(
                    success=False,
                    message="Audit Execution not found."
                )

            self.repository.delete(execution_id)

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Audit Execution deleted successfully."
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to delete Audit Execution: {ex}"
            )

    # =========================================================
    # RESTORE
    # =========================================================

    def restore(self, execution_id):
        try:
            execution = self.repository.restore(execution_id)

            if not execution:
                return ServiceResult(
                    success=False,
                    message="Audit Execution not found."
                )

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Audit Execution restored successfully.",
                data=execution
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to restore Audit Execution: {ex}"
            )