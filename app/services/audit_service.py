from app.models.audit import Audit
from datetime import datetime
from app.repositories.audit_repository import AuditRepository
from app.repositories.audit_type_repository import AuditTypeRepository
from app.repositories.audit_category_repository import AuditCategoryRepository
from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult


class AuditService(BaseService, BaseExportService):
    """
    Business Logic Audit
    """

    EXPORT_CONFIG = [
        {
            "header": "Audit No",
            "field": "audit_no",
            "width": 20,
        },
        {
            "header": "Title",
            "field": "title",
            "width": 35,
        },
        {
            "header": "Audit Type",
            "field": "audit_type_name",
            "width": 25,
        },
        {
            "header": "Audit Category",
            "field": "audit_category_name",
            "width": 25,
        },
        {
            "header": "Audit Date",
            "field": "audit_date",
            "width": 15,
        },
        {
            "header": "Status",
            "field": "status",
            "width": 20,
        },
        {
            "header": "Active",
            "field": "is_active",
            "width": 15,
        },
    ]

    def __init__(self):
        self.repository = AuditRepository()
        self.audit_type_repository = AuditTypeRepository()
        self.audit_category_repository = AuditCategoryRepository()
        self.transaction = TransactionManager()

    # ============================================================
    # GET ALL
    # ============================================================

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

    # ============================================================
    # GET BY ID
    # ============================================================

    def get_by_id(self, audit_id):
        return self.repository.get_by_id(
            audit_id
        )

    # ============================================================
    # GET AUDIT TYPE LIST
    # ============================================================

    def get_audit_types(self):
        return self.audit_type_repository.get_all(
            is_active=True,
            page=1,
            per_page=1000,
        )

    # ============================================================
    # GET AUDIT CATEGORY LIST
    # ============================================================

    def get_audit_categories(self):
        return self.audit_category_repository.get_all(
            is_active=True,
            page=1,
            per_page=1000,
        )

    # ============================================================
    # CREATE
    # ============================================================

    # ============================================================
    # CREATE
    # ============================================================

    def create(
        self,
        title,
        audit_type_id,
        audit_category_id,
        audit_date,
        description=None,
        status="DRAFT",
    ):
        # --------------------------------------------------------
        # Validate Title
        # --------------------------------------------------------

        title = (title or "").strip()

        if not title:
            raise ValueError(
                "Audit Title is required."
            )

        # --------------------------------------------------------
        # Validate Audit Type
        # --------------------------------------------------------

        audit_type = (
            self.audit_type_repository.get_by_id(
                audit_type_id
            )
        )

        if not audit_type:
            raise ValueError(
                "Audit Type not found."
            )

        # --------------------------------------------------------
        # Validate Audit Category
        # --------------------------------------------------------

        audit_category = (
            self.audit_category_repository.get_by_id(
                audit_category_id
            )
        )

        if not audit_category:
            raise ValueError(
                "Audit Category not found."
            )

        # --------------------------------------------------------
        # Validate Audit Date
        # --------------------------------------------------------

        if not audit_date:
            raise ValueError(
                "Audit Date is required."
            )

        # --------------------------------------------------------
        # Validate Status
        # --------------------------------------------------------

        allowed_statuses = [
            "DRAFT",
            "PLANNED",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED",
        ]

        if status not in allowed_statuses:
            raise ValueError(
                "Invalid Audit Status."
            )

        # --------------------------------------------------------
        # Generate Audit No Automatically
        # --------------------------------------------------------

        audit_no = self.generate_audit_no()

        # --------------------------------------------------------
        # Create Audit
        # --------------------------------------------------------

        audit = Audit(
            audit_no=audit_no,
            title=title,
            audit_type_id=audit_type_id,
            audit_category_id=audit_category_id,
            audit_date=audit_date,
            description=description,
            status=status,
        )

        self.repository.create(audit)

        self.transaction.commit()

        return audit

    # ============================================================
    # UPDATE
    # ============================================================

    def update(
        self,
        audit,
        title,
        audit_type_id,
        audit_category_id,
        audit_date,
        description,
        status,
    ):

        if not audit:
            raise ValueError(
                "Audit not found."
            )

        title = (title or "").strip()

        # --------------------------------------------------------
        # Validate Title
        # --------------------------------------------------------

        if not title:
            raise ValueError(
                "Audit Title is required."
            )

        # --------------------------------------------------------
        # Validate Audit Type
        # --------------------------------------------------------

        audit_type = (
            self.audit_type_repository.get_by_id(
                audit_type_id
            )
        )

        if not audit_type:
            raise ValueError(
                "Audit Type not found."
            )

        # --------------------------------------------------------
        # Validate Audit Category
        # --------------------------------------------------------

        audit_category = (
            self.audit_category_repository.get_by_id(
                audit_category_id
            )
        )

        if not audit_category:
            raise ValueError(
                "Audit Category not found."
            )

        # --------------------------------------------------------
        # Validate Audit Date
        # --------------------------------------------------------

        if not audit_date:
            raise ValueError(
                "Audit Date is required."
            )

        # --------------------------------------------------------
        # Validate Status
        # --------------------------------------------------------

        allowed_statuses = [
            "DRAFT",
            "PLANNED",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED",
        ]

        if status not in allowed_statuses:
            raise ValueError(
                "Invalid Audit Status."
            )

        # --------------------------------------------------------
        # Update
        # --------------------------------------------------------

        audit.title = title
        audit.audit_type_id = audit_type_id
        audit.audit_category_id = audit_category_id
        audit.audit_date = audit_date
        audit.description = description
        audit.status = status

        self.repository.update(audit)

        self.transaction.commit()

        return audit

    # ============================================================
    # DELETE
    # ============================================================

    def delete(self, audit):

        self.repository.delete(audit)

        self.transaction.commit()

    # ============================================================
    # EXPORT EXCEL
    # ============================================================

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):

        return self.export(
            sheet_name="Audit",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    # ============================================================
    # GET INACTIVE
    # ============================================================

    def get_inactive(self):

        return self.repository.get_inactive()

    # ============================================================
    # RESTORE
    # ============================================================

    def restore(self, audit_id):

        audit = self.repository.restore(
            audit_id
        )

        if not audit:

            return ServiceResult(
                success=False,
                message="Audit not found.",
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Audit restored successfully.",
        )

    # ============================================================
    # GENERATE AUDIT NO
    # ============================================================

    def generate_audit_no(self):

        year = datetime.now().year

        last_audit = self.repository.get_last_audit_no(
            year
        )

        if not last_audit:

            sequence = 1

        else:

            try:

                last_number = int(
                    last_audit.audit_no[-4:]
                )

                sequence = last_number + 1

            except (ValueError, TypeError):

                sequence = 1

        return f"AUD{year}{sequence:04d}"