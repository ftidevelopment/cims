from app.extensions import db
from sqlalchemy import or_
from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult


class DepartmentService(BaseService, BaseExportService):
    """
    Business Logic Department
    """
    EXPORT_CONFIG = [
        {
            "header": "Department Code",
            "field": "department_code",
            "width": 20,
        },
        {
            "header": "Department Name",
            "field": "department_name",
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
        self.repository = DepartmentRepository()
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


    def get_by_id(self, department_id):
        return self.repository.get_by_id(department_id)

    def create(
        self,
        department_code,
        department_name,
        description=None,
    ):
        # Validasi Department Code
        if self.repository.get_by_code(department_code):
            raise ValueError(
                "Department code already exists."
            )

        department = Department(
            department_code=department_code,
            department_name=department_name,
            description=description,
        )

        self.repository.create(department)

        self.transaction.commit()

        return department

    def update(
        self,
        department,
        department_name,
        description,
    ):
        department.department_name = department_name
        department.description = description

        self.repository.update(department)

        self.transaction.commit()

        return department

    def delete(
        self,
        department,
    ):
        self.repository.delete(department)

        self.transaction.commit()


    def apply_search(self, query, keyword):

        keyword = f"%{keyword}%"

        return query.filter(
            or_(
                self.model.department_code.ilike(keyword),
                self.model.department_name.ilike(keyword),
                self.model.description.ilike(keyword),
            )
        )

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):
        return self.export(
            sheet_name="Department",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_inactive(self):
        return self.repository.get_inactive()


    def restore(self, department_id):
        department = self.repository.restore(department_id)

        if not department:
            return ServiceResult(
                success=False,
                message="Department not found."
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Department restored successfully."
        )
    

    