from app.extensions import db
from app.models.base_model import BaseModel


class AuditChecklist(BaseModel):
    """
    Master Audit Checklist.

    Checklist merupakan master yang dapat digunakan
    pada saat Audit Execution.
    """

    __tablename__ = "audit_checklists"

    audit_checklist_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
    )

    audit_checklist_name = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    items = db.relationship(
        "AuditChecklistItem",
        back_populates="audit_checklist",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="AuditChecklistItem.sort_order",
    )

    audit_executions = db.relationship(
        "AuditExecution",
        back_populates="audit_checklist",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<AuditChecklist "
            f"id={self.id}, "
            f"audit_checklist_code='{self.audit_checklist_code}', "
            f"audit_checklist_name='{self.audit_checklist_name}'>"
        )