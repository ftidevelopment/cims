from app.extensions import db
from app.models.base_model import BaseModel


class AuditChecklistItem(BaseModel):
    """
    Detail item dari Audit Checklist.
    """

    __tablename__ = "audit_checklist_items"

    audit_checklist_id = db.Column(
        db.Integer,
        db.ForeignKey("audit_checklists.id"),
        nullable=False,
    )

    item_no = db.Column(
        db.Integer,
        nullable=False,
    )

    question = db.Column(
        db.String(500),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    is_required = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    sort_order = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    audit_checklist = db.relationship(
        "AuditChecklist",
        back_populates="items",
        lazy="select",
    )

    execution_items = db.relationship(
        "AuditExecutionItem",
        back_populates="audit_checklist_item",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<AuditChecklistItem "
            f"id={self.id}, "
            f"audit_checklist_id={self.audit_checklist_id}, "
            f"item_no={self.item_no}>"
        )