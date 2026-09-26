from app.models.problem_category import ProblemCategory
from app.repositories.problem_category_repository import ProblemCategoryRepository
from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult


class ProblemCategoryService(BaseService, BaseExportService):
    """
    Business Logic ProblemCategory
    """
    EXPORT_CONFIG = [
        {
            "header": "Problem Category Code",
            "field": "problem_category_code",
            "width": 20,
        },
        {
            "header": "Problem Category Name",
            "field": "problem_category_name",
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
        self.repository = ProblemCategoryRepository()
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


    def get_by_id(self, problem_category_id):
        return self.repository.get_by_id(problem_category_id)

    def create(
        self,
        problem_category_code,
        problem_category_name,
        description=None,
    ):
        # Validasi ProblemCategory Code
        if self.repository.exists_by_code(problem_category_code):
            raise ValueError(
                "Problem Category code already exists."
            )

        if self.repository.get_by_name(problem_category_name):
            raise ValueError(
                "Problem Category name already exists."
            )

        problem_category = ProblemCategory(
            problem_category_code=problem_category_code,
            problem_category_name=problem_category_name,
            description=description,
        )

        self.repository.create(problem_category)

        self.transaction.commit()

        return problem_category

    def update(
        self,
        problem_category,
        problem_category_name,
        description,
    ):
        if not problem_category:
            raise ValueError(
                "Problem category not found."
            )

        existing = self.repository.exists_by_name(problem_category_name)

        if existing and existing.id != problem_category.id:
            raise ValueError(
                "Problem Category Name already exists."
            )        
        
        problem_category.problem_category_name = problem_category_name
        problem_category.description = description

        self.repository.update(problem_category)

        self.transaction.commit()

        return problem_category

    def delete(
        self,
        problem_category,
    ):
        self.repository.delete(problem_category)

        self.transaction.commit()


    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):
        return self.export(
            sheet_name="Problem Category",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_inactive(self):
        return self.repository.get_inactive()


    def restore(self, problem_category_id):
        problem_category = self.repository.restore(problem_category_id)

        if not problem_category:
            return ServiceResult(
                success=False,
                message="Problem Category not found."
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Problem Category restored successfully."
        )
    

    