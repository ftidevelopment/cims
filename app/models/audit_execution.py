from app.extensions import db
from app.models.base_model import BaseModel


class AuditExecution(BaseModel):
    """
    Audit Execution / pelaksanaan audit.

    Audit Execution menghubungkan:
    - Audit Assignment
    - Audit Checklist

    Satu Audit Assignment dapat memiliki satu atau lebih
    Audit Execution sesuai kebutuhan pelaksanaan audit.
    """

    __tablename__ = "audit_executions"

    audit_assignment_id = db.Column(
        db.Integer,
        db.ForeignKey("audit_assignments.id"),
        nullable=False,
    )

    audit_checklist_id = db.Column(
        db.Integer,
        db.ForeignKey("audit_checklists.id"),
        nullable=False,
    )

    execution_date = db.Column(
        db.Date,
        nullable=False,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="NOT_STARTED",
    )

    started_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    remark = db.Column(
        db.Text,
        nullable=True,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    audit_assignment = db.relationship(
        "AuditAssignment",
        back_populates="audit_executions",
        lazy="select",
    )

    audit_checklist = db.relationship(
        "AuditChecklist",
        back_populates="audit_executions",
        lazy="select",
    )

    items = db.relationship(
        "AuditExecutionItem",
        back_populates="audit_execution",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="AuditExecutionItem.item_no",
    )

    findings = db.relationship(
        "AuditFinding",
        back_populates="audit_execution",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<AuditExecution "
            f"id={self.id}, "
            f"audit_assignment_id={self.audit_assignment_id}, "
            f"audit_checklist_id={self.audit_checklist_id}, "
            f"execution_date='{self.execution_date}', "
            f"status='{self.status}'>"
        )