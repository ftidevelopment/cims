from app.models.kaizen_category import KaizenCategory
from app.repositories.kaizen_category_repository import KaizenCategoryRepository
from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult


class KaizenCategoryService(BaseService, BaseExportService):
    """
    Business Logic KaizenCategory
    """

    EXPORT_CONFIG = [
        {
            "header": "Kaizen Category Code",
            "field": "kaizen_category_code",
            "width": 20,
        },
        {
            "header": "Kaizen Category Name",
            "field": "kaizen_category_name",
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
        self.repository = KaizenCategoryRepository()
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

    def get_by_id(self, kaizen_category_id):
        return self.repository.get_by_id(kaizen_category_id)

    def create(
        self,
        kaizen_category_code,
        kaizen_category_name,
        description=None,
    ):
        # Validasi Kaizen Category Code
        if self.repository.exists_by_code(
            kaizen_category_code
        ):
            raise ValueError(
                "Kaizen Category code already exists."
            )

        # Validasi Kaizen Category Name
        if self.repository.get_by_name(
            kaizen_category_name
        ):
            raise ValueError(
                "Kaizen Category name already exists."
            )

        kaizen_category = KaizenCategory(
            kaizen_category_code=kaizen_category_code,
            kaizen_category_name=kaizen_category_name,
            description=description,
        )

        self.repository.create(kaizen_category)

        self.transaction.commit()

        return kaizen_category

    def update(
        self,
        kaizen_category,
        kaizen_category_name,
        description,
    ):
        if not kaizen_category:
            raise ValueError(
                "Kaizen category not found."
            )

        existing = self.repository.exists_by_name(
            kaizen_category_name
        )

        if existing and existing.id != kaizen_category.id:
            raise ValueError(
                "Kaizen Category Name already exists."
            )

        kaizen_category.kaizen_category_name = (
            kaizen_category_name
        )

        kaizen_category.description = description

        self.repository.update(kaizen_category)

        self.transaction.commit()

        return kaizen_category

    def delete(
        self,
        kaizen_category,
    ):
        self.repository.delete(kaizen_category)

        self.transaction.commit()

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):
        return self.export(
            sheet_name="Kaizen Category",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_inactive(self):
        return self.repository.get_inactive()

    def restore(self, kaizen_category_id):
        kaizen_category = self.repository.restore(
            kaizen_category_id
        )

        if not kaizen_category:
            return ServiceResult(
                success=False,
                message="Kaizen Category not found."
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Kaizen Category restored successfully."
        )