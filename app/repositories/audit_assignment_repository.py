from app.models.audit_assignment import AuditAssignment
from app.repositories.base_repository import BaseRepository


class AuditAssignmentRepository(BaseRepository):

    model = AuditAssignment

    searchable_fields = [
        AuditAssignment.location,
    ]

    sortable_fields = {
        "location": AuditAssignment.location,
        "created_at": AuditAssignment.created_at,
    }

    def __init__(self):
        super().__init__(AuditAssignment)

    def get_by_audit(self, audit_id: int):
        return (
            self.model.query
            .filter_by(
                audit_id=audit_id,
                is_active=True,
            )
            .order_by(
                self.model.location.asc(),
                self.model.auditor_employee_id.asc(),
            )
            .all()
        )

    def get_by_auditor(self, auditor_employee_id: int):
        return (
            self.model.query
            .filter_by(
                auditor_employee_id=auditor_employee_id,
                is_active=True,
            )
            .all()
        )

    def get_by_location(self, audit_id: int, location: str):
        return (
            self.model.query
            .filter_by(
                audit_id=audit_id,
                location=location,
                is_active=True,
            )
            .all()
        )

    def get_assignment(
        self,
        audit_id: int,
        auditor_employee_id: int,
        location: str,
    ):
        return (
            self.model.query
            .filter_by(
                audit_id=audit_id,
                auditor_employee_id=auditor_employee_id,
                location=location,
                is_active=True,
            )
            .first()
        )

    def exists_assignment(
        self,
        audit_id: int,
        auditor_employee_id: int,
        location: str,
    ) -> bool:

        return (
            self.get_assignment(
                audit_id=audit_id,
                auditor_employee_id=auditor_employee_id,
                location=location,
            )
            is not None
        )

    def get_auditors_by_location(
        self,
        audit_id: int,
        location: str,
    ):
        return (
            self.model.query
            .filter_by(
                audit_id=audit_id,
                location=location,
                is_active=True,
            )
            .all()
        )

    def get_locations_by_auditor(
        self,
        audit_id: int,
        auditor_employee_id: int,
    ):
        return (
            self.model.query
            .filter_by(
                audit_id=audit_id,
                auditor_employee_id=auditor_employee_id,
                is_active=True,
            )
            .all()
        )