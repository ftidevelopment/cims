from app.models.audit_category import AuditCategory
from app.repositories.audit_category_repository import AuditCategoryRepository
from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult


class AuditCategoryService(BaseService, BaseExportService):
    """
    Business Logic AuditCategory
    """

    EXPORT_CONFIG = [
        {
            "header": "Audit Category Code",
            "field": "audit_category_code",
            "width": 20,
        },
        {
            "header": "Audit Category Name",
            "field": "audit_category_name",
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
        self.repository = AuditCategoryRepository()
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

    def get_by_id(self, audit_category_id):
        return self.repository.get_by_id(audit_category_id)

    def create(
        self,
        audit_category_code,
        audit_category_name,
        description=None,
    ):
        if self.repository.exists_by_code(audit_category_code):
            raise ValueError(
                "Audit Category code already exists."
            )

        if self.repository.exists_by_name(audit_category_name):
            raise ValueError(
                "Audit Category name already exists."
            )

        audit_category = AuditCategory(
            audit_category_code=audit_category_code,
            audit_category_name=audit_category_name,
            description=description,
        )

        self.repository.create(audit_category)
        self.transaction.commit()

        return audit_category

    def update(
        self,
        audit_category,
        audit_category_name,
        description,
    ):
        if not audit_category:
            raise ValueError(
                "Audit Category not found."
            )

        existing = self.repository.get_by_name(
            audit_category_name
        )

        if existing and existing.id != audit_category.id:
            raise ValueError(
                "Audit Category name already exists."
            )

        audit_category.audit_category_name = audit_category_name
        audit_category.description = description

        self.repository.update(audit_category)
        self.transaction.commit()

        return audit_category

    def delete(self, audit_category):
        self.repository.delete(audit_category)
        self.transaction.commit()

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):
        return self.export(
            sheet_name="Audit Category",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_inactive(self):
        return self.repository.get_inactive()

    def restore(self, audit_category_id):
        audit_category = self.repository.restore(
            audit_category_id
        )

        if not audit_category:
            return ServiceResult(
                success=False,
                message="Audit Category not found.",
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Audit Category restored successfully.",
        )