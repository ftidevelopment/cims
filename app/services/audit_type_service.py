from app.models.audit_type import AuditType
from app.repositories.audit_type_repository import AuditTypeRepository
from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult


class AuditTypeService(BaseService, BaseExportService):
    """
    Business Logic AuditType
    """

    EXPORT_CONFIG = [
        {
            "header": "Audit Type Code",
            "field": "audit_type_code",
            "width": 20,
        },
        {
            "header": "Audit Type Name",
            "field": "audit_type_name",
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
        self.repository = AuditTypeRepository()
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

    def get_by_id(self, audit_type_id):

        return self.repository.get_by_id(
            audit_type_id
        )

    def create(
        self,
        audit_type_code,
        audit_type_name,
        description=None,
    ):

        # Validasi Audit Type Code
        if self.repository.exists_by_code(
            audit_type_code
        ):
            raise ValueError(
                "Audit Type code already exists."
            )

        # Validasi Audit Type Name
        if self.repository.exists_by_name(
            audit_type_name
        ):
            raise ValueError(
                "Audit Type name already exists."
            )

        audit_type = AuditType(
            audit_type_code=audit_type_code,
            audit_type_name=audit_type_name,
            description=description,
        )

        self.repository.create(audit_type)

        self.transaction.commit()

        return audit_type

    def update(
        self,
        audit_type,
        audit_type_name,
        description,
    ):

        if not audit_type:
            raise ValueError(
                "Audit Type not found."
            )

        existing = self.repository.get_by_name(
            audit_type_name
        )

        if existing and existing.id != audit_type.id:
            raise ValueError(
                "Audit Type name already exists."
            )

        audit_type.audit_type_name = audit_type_name
        audit_type.description = description

        self.repository.update(audit_type)

        self.transaction.commit()

        return audit_type

    def delete(
        self,
        audit_type,
    ):

        self.repository.delete(audit_type)

        self.transaction.commit()

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):

        return self.export(
            sheet_name="Audit Type",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_inactive(self):

        return self.repository.get_inactive()

    def restore(
        self,
        audit_type_id,
    ):

        audit_type = self.repository.restore(
            audit_type_id
        )

        if not audit_type:
            return ServiceResult(
                success=False,
                message="Audit Type not found."
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Audit Type restored successfully."
        )