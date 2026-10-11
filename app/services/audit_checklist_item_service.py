from app.models.audit_checklist_item import AuditChecklistItem
from app.repositories.audit_checklist_item_repository import (
    AuditChecklistItemRepository,
)
from app.repositories.audit_checklist_repository import (
    AuditChecklistRepository,
)
from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult

class AuditChecklistItemService:

    def __init__(self):
        self.repository = AuditChecklistItemRepository()
        self.checklist_repository = AuditChecklistRepository()
        self.transaction = TransactionManager()

    def get_by_id(self, item_id):
        return self.repository.get_by_id(item_id)

    def get_by_checklist(self, audit_checklist_id):
        return self.repository.get_by_checklist(
            audit_checklist_id
        )

    def get_by_item_no(
        self,
        audit_checklist_id,
        item_no,
    ):
        return self.repository.get_by_item_no(
            audit_checklist_id=audit_checklist_id,
            item_no=item_no,
        )

    def create(
        self,
        audit_checklist_id,
        question,
        description=None,
        is_required=True,
        item_no=None,
        sort_order=None,
    ):
        # --------------------------------------------------
        # Validate Checklist
        # --------------------------------------------------

        checklist = self.checklist_repository.get_by_id(
            audit_checklist_id
        )

        if not checklist:
            raise ValueError(
                "Audit Checklist not found."
            )

        # --------------------------------------------------
        # Validate Question
        # --------------------------------------------------

        question = (question or "").strip()

        if not question:
            raise ValueError(
                "Checklist Question is required."
            )

        # --------------------------------------------------
        # Generate Item No
        # --------------------------------------------------

        if item_no is None:
            last_item = self.repository.get_last_item_no(
                audit_checklist_id
            )

            if last_item:
                item_no = last_item.item_no + 1
            else:
                item_no = 1

        try:
            item_no = int(item_no)
        except (TypeError, ValueError):
            raise ValueError(
                "Item No must be a valid number."
            )

        if item_no <= 0:
            raise ValueError(
                "Item No must be greater than zero."
            )

        # --------------------------------------------------
        # Check Duplicate Item No
        # --------------------------------------------------

        if self.repository.exists_by_item_no(
            audit_checklist_id=audit_checklist_id,
            item_no=item_no,
        ):
            raise ValueError(
                "Item No already exists in this checklist."
            )

        # --------------------------------------------------
        # Generate Sort Order
        # --------------------------------------------------

        if sort_order is None:
            last_sort = self.repository.get_last_sort_order(
                audit_checklist_id
            )

            if last_sort:
                sort_order = last_sort.sort_order + 1
            else:
                sort_order = 1

        try:
            sort_order = int(sort_order)
        except (TypeError, ValueError):
            raise ValueError(
                "Sort Order must be a valid number."
            )

        if sort_order <= 0:
            raise ValueError(
                "Sort Order must be greater than zero."
            )

        # --------------------------------------------------
        # Create Item
        # --------------------------------------------------

        item = AuditChecklistItem(
            audit_checklist_id=audit_checklist_id,
            item_no=item_no,
            question=question,
            description=description,
            is_required=bool(is_required),
            sort_order=sort_order,
        )

        self.repository.create(item)
        self.transaction.commit()

        return item

    def update(
        self,
        item,
        question,
        description=None,
        is_required=True,
        item_no=None,
        sort_order=None,
    ):
        if not item:
            raise ValueError(
                "Audit Checklist Item not found."
            )

        # --------------------------------------------------
        # Validate Question
        # --------------------------------------------------

        question = (question or "").strip()

        if not question:
            raise ValueError(
                "Checklist Question is required."
            )

        # --------------------------------------------------
        # Item No
        # --------------------------------------------------

        if item_no is None:
            item_no = item.item_no

        try:
            item_no = int(item_no)
        except (TypeError, ValueError):
            raise ValueError(
                "Item No must be a valid number."
            )

        if item_no <= 0:
            raise ValueError(
                "Item No must be greater than zero."
            )

        # --------------------------------------------------
        # Check Duplicate Item No
        # --------------------------------------------------

        existing = self.repository.get_by_item_no(
            audit_checklist_id=item.audit_checklist_id,
            item_no=item_no,
        )

        if existing and existing.id != item.id:
            raise ValueError(
                "Item No already exists in this checklist."
            )

        # --------------------------------------------------
        # Sort Order
        # --------------------------------------------------

        if sort_order is None:
            sort_order = item.sort_order

        try:
            sort_order = int(sort_order)
        except (TypeError, ValueError):
            raise ValueError(
                "Sort Order must be a valid number."
            )

        if sort_order <= 0:
            raise ValueError(
                "Sort Order must be greater than zero."
            )

        # --------------------------------------------------
        # Update
        # --------------------------------------------------

        item.item_no = item_no
        item.question = question
        item.description = description
        item.is_required = bool(is_required)
        item.sort_order = sort_order

        self.repository.update(item)
        self.transaction.commit()

        return item

    def delete(self, item):
        if not item:
            raise ValueError(
                "Audit Checklist Item not found."
            )

        self.repository.delete(item)
        self.transaction.commit()

    def delete_by_checklist(
        self,
        audit_checklist_id,
    ):
        items = self.repository.get_by_checklist(
            audit_checklist_id
        )

        for item in items:
            self.repository.delete(item)

        if items:
            self.transaction.commit()

        return len(items)

    def get_by_checklist_status(
        self,
        audit_checklist_id,
        is_active=None,
    ):
        return self.repository.get_by_checklist_status(
            audit_checklist_id=audit_checklist_id,
            is_active=is_active,
        )

    def restore(self, item_id):
        item = self.repository.restore(item_id)

        if not item:
            return ServiceResult(
                success=False,
                message="Audit Checklist Item not found.",
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Audit Checklist Item restored successfully.",
        )