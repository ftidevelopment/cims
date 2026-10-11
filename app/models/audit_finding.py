from app.extensions import db
from app.models.base_model import BaseModel


class AuditFinding(BaseModel):
    __tablename__ = "audit_findings"

    # ============================================================
    # Finding Information
    # ============================================================

    finding_no = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    audit_execution_id = db.Column(
        db.Integer,
        db.ForeignKey("audit_executions.id"),
        nullable=False
    )

    # NULL apabila finding berasal dari luar checklist
    audit_execution_item_id = db.Column(
        db.Integer,
        db.ForeignKey("audit_execution_items.id"),
        nullable=True
    )

    # CHECKLIST / OUTSIDE_CHECKLIST
    finding_source = db.Column(
        db.String(30),
        nullable=False
    )

    finding = db.Column(
        db.Text,
        nullable=False
    )

    # CRITICAL / MAJOR / MINOR / OBSERVATION
    severity = db.Column(
        db.String(20),
        nullable=False
    )

    # ============================================================
    # Corrective Action
    # ============================================================

    # PIC finding/action
    pic_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=True
    )

    target_date = db.Column(
        db.Date,
        nullable=True
    )

    # OPEN / IN_PROGRESS / ACTION_COMPLETED /
    # AUDITOR_VERIFICATION / PASS / CLOSED
    status = db.Column(
        db.String(30),
        nullable=False,
        default="OPEN"
    )

    corrective_action = db.Column(
        db.Text,
        nullable=True
    )

    action_completed_date = db.Column(
        db.Date,
        nullable=True
    )

    # ============================================================
    # Verification
    # ============================================================

    verification_result = db.Column(
        db.Text,
        nullable=True
    )

    # PASS / FAIL
    verification_status = db.Column(
        db.String(10),
        nullable=True
    )

    verified_by_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=True
    )

    verified_date = db.Column(
        db.Date,
        nullable=True
    )

    # ============================================================
    # Relationships
    # ============================================================

    audit_execution = db.relationship(
        "AuditExecution",
        back_populates="findings",
        lazy="select"
    )

    audit_execution_item = db.relationship(
        "AuditExecutionItem",
        back_populates="findings",
        lazy="select"
    )

    pic_employee = db.relationship(
        "Employee",
        foreign_keys=[pic_employee_id],
        lazy="select"
    )

    verified_by_employee = db.relationship(
        "Employee",
        foreign_keys=[verified_by_employee_id],
        lazy="select"
    )

    attachments = db.relationship(
        "AuditFindingAttachment",
        back_populates="audit_finding",
        lazy="select",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self):
        return (
            f"<AuditFinding "
            f"id={self.id}, "
            f"finding_no='{self.finding_no}', "
            f"finding_source='{self.finding_source}', "
            f"severity='{self.severity}', "
            f"status='{self.status}'>"
        )