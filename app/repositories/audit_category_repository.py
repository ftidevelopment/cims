from app.models.audit_category import AuditCategory
from app.repositories.base_repository import BaseRepository


class AuditCategoryRepository(BaseRepository):

    model = AuditCategory

    searchable_fields = [
        AuditCategory.audit_category_code,
        AuditCategory.audit_category_name,
        AuditCategory.description,
    ]

    sortable_fields = {
        "audit_category_code": AuditCategory.audit_category_code,
        "audit_category_name": AuditCategory.audit_category_name,
        "description": AuditCategory.description,
        "created_at": AuditCategory.created_at,
    }

    def __init__(self):
        super().__init__(AuditCategory)

    def get_by_code(self, audit_category_code: str):
        return self.get_first_by(
            audit_category_code=audit_category_code
        )

    def get_by_name(self, audit_category_name: str):
        return self.get_first_by(
            audit_category_name=audit_category_name
        )

    def exists_by_code(self, audit_category_code: str) -> bool:
        return self.get_by_code(audit_category_code) is not None

    def exists_by_name(self, audit_category_name: str) -> bool:
        return self.get_by_name(audit_category_name) is not None