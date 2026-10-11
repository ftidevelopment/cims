from app.models.audit_checklist import AuditChecklist
from app.repositories.base_repository import BaseRepository


class AuditChecklistRepository(BaseRepository):
    model = AuditChecklist

    searchable_fields = [
        AuditChecklist.audit_checklist_code,
        AuditChecklist.audit_checklist_name,
        AuditChecklist.description,
    ]

    sortable_fields = {
        "audit_checklist_code": AuditChecklist.audit_checklist_code,
        "audit_checklist_name": AuditChecklist.audit_checklist_name,
        "description": AuditChecklist.description,
        "created_at": AuditChecklist.created_at,
    }

    def __init__(self):
        super().__init__(AuditChecklist)

    def get_by_code(self, audit_checklist_code: str):
        return self.get_first_by(
            audit_checklist_code=audit_checklist_code
        )

    def get_by_name(self, audit_checklist_name: str):
        return self.get_first_by(
            audit_checklist_name=audit_checklist_name
        )

    def exists_by_code(self, audit_checklist_code: str) -> bool:
        return self.get_by_code(audit_checklist_code) is not None

    def exists_by_name(self, audit_checklist_name: str) -> bool:
        return self.get_by_name(audit_checklist_name) is not None