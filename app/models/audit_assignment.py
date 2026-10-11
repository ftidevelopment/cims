from app.extensions import db
from app.models.base_model import BaseModel


class AuditAssignment(BaseModel):
    """
    Assignment of auditors to a specific location
    within an audit.

    One audit can have multiple auditors.
    One location can have multiple auditors.
    One auditor can be assigned to multiple locations.
    """

    __tablename__ = "audit_assignments"

    # ============================================================
    # AUDIT
    # ============================================================

    audit_id = db.Column(
        db.Integer,
        db.ForeignKey("audits.id"),
        nullable=False,
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False,
    )

    # ============================================================
    # AUDITOR
    # ============================================================

    auditor_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False,
    )

    # ============================================================
    # LOCATION
    # ============================================================

    location = db.Column(
        db.String(200),
        nullable=False,
    )

    # ============================================================
    # RELATIONSHIP - AUDIT
    # ============================================================

    audit = db.relationship(
        "Audit",
        back_populates="audit_assignments",
        lazy="select",
    )

    # ============================================================
    # RELATIONSHIP - DEPARTMENT
    # ============================================================

    department = db.relationship(
        "Department",
        lazy="select",
    )

    # ============================================================
    # RELATIONSHIP - EMPLOYEE / AUDITOR
    # ============================================================

    auditor = db.relationship(
        "Employee",
        back_populates="audit_assignments",
        lazy="select",
    )

    audit_executions = db.relationship(
        "AuditExecution",
        back_populates="audit_assignment",
        lazy="select",
        cascade="all, delete-orphan",
    )

    # ============================================================
    # UNIQUE CONSTRAINT
    # ============================================================

    __table_args__ = (
        db.UniqueConstraint(
            "audit_id",
            "auditor_employee_id",
            "location",
            name="uq_audit_assignment",
        ),
    )

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __repr__(self):
        return (
            f"<AuditAssignment "
            f"id={self.id}, "
            f"audit_id={self.audit_id}, "
            f"auditor_employee_id={self.auditor_employee_id}, "
            f"location='{self.location}'>"
        )