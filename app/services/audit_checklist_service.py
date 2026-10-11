from app.models.audit_checklist import AuditChecklist
from app.repositories.audit_checklist_repository import AuditChecklistRepository
from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult


class AuditChecklistService(BaseService, BaseExportService):

    EXPORT_CONFIG = [
        {
            "header": "Checklist Code",
            "field": "audit_checklist_code",
            "width": 20,
        },
        {
            "header": "Checklist Name",
            "field": "audit_checklist_name",
            "width": 35,
        },
        {
            "header": "Description",
            "field": "description",
            "width": 50,
        },
        {
            "header": "Status",
            "field": "is_active",
            "width": 15,
        },
    ]

    def __init__(self):
        self.repository = AuditChecklistRepository()
        self.transaction = TransactionManager()

    def get_all(
        self,
        keyword=None,
        is_active=True,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="asc",
    ):
        return self.repository.get_all(
            keyword=keyword,
            is_active=is_active,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_by_id(self, audit_checklist_id):
        return self.repository.get_by_id(audit_checklist_id)

    def create(
        self,
        audit_checklist_code,
        audit_checklist_name,
        description=None,
    ):
        audit_checklist_code = (
            audit_checklist_code or ""
        ).strip().upper()

        audit_checklist_name = (
            audit_checklist_name or ""
        ).strip()

        if not audit_checklist_code:
            raise ValueError(
                "Audit Checklist Code is required."
            )

        if not audit_checklist_name:
            raise ValueError(
                "Audit Checklist Name is required."
            )

        if self.repository.exists_by_code(
            audit_checklist_code
        ):
            raise ValueError(
                "Audit Checklist code already exists."
            )

        if self.repository.exists_by_name(
            audit_checklist_name
        ):
            raise ValueError(
                "Audit Checklist name already exists."
            )

        audit_checklist = AuditChecklist(
            audit_checklist_code=audit_checklist_code,
            audit_checklist_name=audit_checklist_name,
            description=description,
        )

        self.repository.create(audit_checklist)
        self.transaction.commit()

        return audit_checklist

    def update(
        self,
        audit_checklist,
        audit_checklist_name,
        description,
    ):
        if not audit_checklist:
            raise ValueError(
                "Audit Checklist not found."
            )

        audit_checklist_name = (
            audit_checklist_name or ""
        ).strip()

        if not audit_checklist_name:
            raise ValueError(
                "Audit Checklist Name is required."
            )

        existing = self.repository.get_by_name(
            audit_checklist_name
        )

        if existing and existing.id != audit_checklist.id:
            raise ValueError(
                "Audit Checklist name already exists."
            )

        audit_checklist.audit_checklist_name = (
            audit_checklist_name
        )

        audit_checklist.description = description

        self.repository.update(audit_checklist)
        self.transaction.commit()

        return audit_checklist

    def delete(self, audit_checklist):
        if not audit_checklist:
            raise ValueError(
                "Audit Checklist not found."
            )

        self.repository.delete(audit_checklist)
        self.transaction.commit()

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):
        return self.export(
            sheet_name="Audit Checklist",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_inactive(self):
        return self.repository.get_inactive()

    def restore(self, audit_checklist_id):
        audit_checklist = self.repository.restore(
            audit_checklist_id
        )

        if not audit_checklist:
            return ServiceResult(
                success=False,
                message="Audit Checklist not found.",
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Audit Checklist restored successfully.",
        )