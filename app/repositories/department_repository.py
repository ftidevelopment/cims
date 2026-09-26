from app.models.department import Department
from app.repositories.base_repository import BaseRepository


class DepartmentRepository(BaseRepository):

    model = Department

    searchable_fields = [
        Department.department_code,
        Department.department_name,
        Department.description,
    ]

    sortable_fields = {
        "department_code": Department.department_code,
        "department_name": Department.department_name,
        "description": Department.description,
        "created_at": Department.created_at,
    }

    def __init__(self):
        super().__init__(Department)

    def get_by_code(
        self,
        department_code: str,
    ):

        return self.get_first_by(
            department_code=department_code,
        )

    def get_by_name(
        self,
        department_name: str,
    ):

        return self.get_first_by(
            department_name=department_name,
        )

    def exists_by_code(self, department_code: str) -> bool:
        return self.get_by_code(department_code) is not None

    def exists_by_name(self, department_name: str) -> bool:
        return self.get_by_name(department_name) is not None