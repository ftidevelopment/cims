from app.models.audit_execution_item import AuditExecutionItem
from app.repositories.base_repository import BaseRepository


class AuditExecutionItemRepository(BaseRepository):
    """
    Repository untuk Audit Execution Item.
    """

    model = AuditExecutionItem

    searchable_fields = [
        AuditExecutionItem.question,
        AuditExecutionItem.result,
        AuditExecutionItem.remark,
    ]

    sortable_fields = {
        "item_no": AuditExecutionItem.item_no,
        "result": AuditExecutionItem.result,
        "created_at": AuditExecutionItem.created_at,
    }

    def __init__(self):
        super().__init__(AuditExecutionItem)

    # ======================================================
    # GET BY EXECUTION
    # ======================================================

    def get_by_execution(
        self,
        audit_execution_id: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_execution_id=audit_execution_id,
                is_active=True,
            )
            .order_by(
                self.model.item_no.asc(),
            )
            .all()
        )

    # ======================================================
    # GET BY CHECKLIST ITEM
    # ======================================================

    def get_by_checklist_item(
        self,
        audit_checklist_item_id: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_checklist_item_id=audit_checklist_item_id,
                is_active=True,
            )
            .order_by(
                self.model.created_at.desc(),
            )
            .all()
        )

    # ======================================================
    # GET ONE ITEM
    # ======================================================

    def get_by_execution_and_checklist_item(
        self,
        audit_execution_id: int,
        audit_checklist_item_id: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_execution_id=audit_execution_id,
                audit_checklist_item_id=audit_checklist_item_id,
                is_active=True,
            )
            .first()
        )

    # ======================================================
    # EXISTS ITEM
    # ======================================================

    def exists_by_execution_and_checklist_item(
        self,
        audit_execution_id: int,
        audit_checklist_item_id: int,
    ) -> bool:
        return (
            self.get_by_execution_and_checklist_item(
                audit_execution_id=audit_execution_id,
                audit_checklist_item_id=audit_checklist_item_id,
            )
            is not None
        )

    # ======================================================
    # GET BY RESULT
    # ======================================================

    def get_by_result(
        self,
        audit_execution_id: int,
        result: str,
    ):
        return (
            self.model.query
            .filter_by(
                audit_execution_id=audit_execution_id,
                result=result,
                is_active=True,
            )
            .order_by(
                self.model.item_no.asc(),
            )
            .all()
        )

    # ======================================================
    # COUNT BY RESULT
    # ======================================================

    def count_by_result(
        self,
        audit_execution_id: int,
        result: str,
    ) -> int:
        return (
            self.model.query
            .filter_by(
                audit_execution_id=audit_execution_id,
                result=result,
                is_active=True,
            )
            .count()
        )