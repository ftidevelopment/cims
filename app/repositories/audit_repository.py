from app.models.audit import Audit
from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository):

    model = Audit

    searchable_fields = [
        Audit.audit_no,
        Audit.title,
        Audit.description,
        Audit.status,
    ]

    sortable_fields = {
        "audit_no": Audit.audit_no,
        "title": Audit.title,
        "audit_date": Audit.audit_date,
        "status": Audit.status,
        "created_at": Audit.created_at,
    }

    def __init__(self):
        super().__init__(Audit)

    # ============================================================
    # GET BY AUDIT NO
    # ============================================================

    def get_by_audit_no(self, audit_no: str):
        return self.get_first_by(
            audit_no=audit_no
        )

    # ============================================================
    # CHECK AUDIT NO
    # ============================================================

    def exists_by_audit_no(self, audit_no: str) -> bool:
        return (
            self.get_by_audit_no(audit_no)
            is not None
        )

    # ============================================================
    # GET LAST AUDIT NO BY YEAR
    # ============================================================

    def get_last_audit_no(self, year: int):

        prefix = f"AUD{year}"

        return (
            self.model.query
            .filter(
                self.model.audit_no.like(
                    f"{prefix}%"
                )
            )
            .order_by(
                self.model.audit_no.desc()
            )
            .first()
        )

    # ============================================================
    # GET BY STATUS
    # ============================================================

    def get_by_status(self, status: str):
        return self.get_all(
            status=status
        )

    # ============================================================
    # GET BY AUDIT TYPE
    # ============================================================

    def get_by_audit_type(self, audit_type_id: int):
        return self.get_all(
            audit_type_id=audit_type_id
        )

    # ============================================================
    # GET BY AUDIT CATEGORY
    # ============================================================

    def get_by_audit_category(
        self,
        audit_category_id: int,
    ):
        return self.get_all(
            audit_category_id=audit_category_id
        )

    # ============================================================
    # GET BY DATE
    # ============================================================

    def get_by_audit_date(self, audit_date):
        return self.get_all(
            audit_date=audit_date
        )