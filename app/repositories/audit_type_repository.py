from app.models.audit_type import AuditType
from app.repositories.base_repository import BaseRepository


class AuditTypeRepository(BaseRepository):

    model = AuditType

    searchable_fields = [
        AuditType.audit_type_code,
        AuditType.audit_type_name,
        AuditType.description,
    ]

    sortable_fields = {
        "audit_type_code": AuditType.audit_type_code,
        "audit_type_name": AuditType.audit_type_name,
        "description": AuditType.description,
        "created_at": AuditType.created_at,
    }

    def __init__(self):
        super().__init__(AuditType)

    def get_by_code(
        self,
        audit_type_code: str,
    ):

        return self.get_first_by(
            audit_type_code=audit_type_code,
        )

    def get_by_name(
        self,
        audit_type_name: str,
    ):

        return self.get_first_by(
            audit_type_name=audit_type_name,
        )

    def exists_by_code(
        self,
        audit_type_code: str,
    ) -> bool:

        return self.get_by_code(audit_type_code) is not None

    def exists_by_name(
        self,
        audit_type_name: str,
    ) -> bool:

        return self.get_by_name(audit_type_name) is not None