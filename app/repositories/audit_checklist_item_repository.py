from app.models.audit_checklist_item import AuditChecklistItem
from app.repositories.base_repository import BaseRepository


class AuditChecklistItemRepository(BaseRepository):
    model = AuditChecklistItem

    searchable_fields = [
        AuditChecklistItem.question,
        AuditChecklistItem.description,
    ]

    sortable_fields = {
        "item_no": AuditChecklistItem.item_no,
        "question": AuditChecklistItem.question,
        "sort_order": AuditChecklistItem.sort_order,
        "created_at": AuditChecklistItem.created_at,
    }

    def __init__(self):
        super().__init__(AuditChecklistItem)

    def get_by_checklist(self, audit_checklist_id: int):
        return (
            self.model.query
            .filter_by(
                audit_checklist_id=audit_checklist_id,
                is_active=True,
            )
            .order_by(
                self.model.sort_order.asc(),
                self.model.item_no.asc(),
            )
            .all()
        )

    def get_by_item_no(
        self,
        audit_checklist_id: int,
        item_no: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_checklist_id=audit_checklist_id,
                item_no=item_no,
                is_active=True,
            )
            .first()
        )

    def exists_by_item_no(
        self,
        audit_checklist_id: int,
        item_no: int,
    ) -> bool:
        return (
            self.get_by_item_no(
                audit_checklist_id=audit_checklist_id,
                item_no=item_no,
            )
            is not None
        )

    def get_last_item_no(
        self,
        audit_checklist_id: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_checklist_id=audit_checklist_id,
                is_active=True,
            )
            .order_by(self.model.item_no.desc())
            .first()
        )

    def get_last_sort_order(
        self,
        audit_checklist_id: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_checklist_id=audit_checklist_id,
                is_active=True,
            )
            .order_by(self.model.sort_order.desc())
            .first()
        )

    def get_by_checklist_status(
        self,
        audit_checklist_id: int,
        is_active=None,
    ):
        query = (
            self.model.query
            .filter_by(
                audit_checklist_id=audit_checklist_id
            )
        )

        if is_active is not None:
            query = query.filter_by(
                is_active=is_active
            )

        return (
            query
            .order_by(
                self.model.sort_order.asc(),
                self.model.item_no.asc(),
            )
            .all()
        )