from app.extensions import db
from app.models.base_model import BaseModel


class AuditExecutionItem(BaseModel):
    """
    Hasil pelaksanaan satu item checklist.

    Data question disimpan sebagai snapshot agar hasil audit
    lama tetap mempertahankan pertanyaan yang digunakan saat
    audit dilakukan, meskipun master checklist berubah
    di kemudian hari.
    """

    __tablename__ = "audit_execution_items"

    audit_execution_id = db.Column(
        db.Integer,
        db.ForeignKey("audit_executions.id"),
        nullable=False,
    )

    audit_checklist_item_id = db.Column(
        db.Integer,
        db.ForeignKey("audit_checklist_items.id"),
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

    result = db.Column(
        db.String(10),
        nullable=True,
    )

    remark = db.Column(
        db.Text,
        nullable=True,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    audit_execution = db.relationship(
        "AuditExecution",
        back_populates="items",
        lazy="select",
    )

    audit_checklist_item = db.relationship(
        "AuditChecklistItem",
        back_populates="execution_items",
        lazy="select",
    )

    findings = db.relationship(
        "AuditFinding",
        back_populates="audit_execution_item",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<AuditExecutionItem "
            f"id={self.id}, "
            f"audit_execution_id={self.audit_execution_id}, "
            f"item_no={self.item_no}, "
            f"result='{self.result}'>"
        )