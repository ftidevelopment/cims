from app.extensions import db
from app.models.base_model import BaseModel


class Audit(BaseModel):
    """
    Audit transaction model.

    Audit Type dan Audit Category merupakan master data
    yang berdiri sendiri dan dipilih pada saat membuat Audit.
    """

    __tablename__ = "audits"

    # ============================================================
    # AUDIT NUMBER
    # ============================================================

    audit_no = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
    )

    # ============================================================
    # BASIC INFORMATION
    # ============================================================

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # AUDIT TYPE
    # ============================================================

    audit_type_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "audit_types.id"
        ),
        nullable=False,
    )

    # ============================================================
    # AUDIT CATEGORY
    # ============================================================

    audit_category_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "audit_categories.id"
        ),
        nullable=False,
    )

    # ============================================================
    # AUDIT DATE
    # ============================================================

    audit_date = db.Column(
        db.Date,
        nullable=False,
    )

    # ============================================================
    # STATUS
    # ============================================================

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT",
    )

    # ============================================================
    # RELATIONSHIP
    # ============================================================

    audit_type = db.relationship(
        "AuditType",
        back_populates="audits",
        lazy="select",
    )

    audit_category = db.relationship(
        "AuditCategory",
        back_populates="audits",
        lazy="select",
    )

    audit_assignments = db.relationship(
        "AuditAssignment",
        back_populates="audit",
        lazy="select",
        cascade="all, delete-orphan",
    )

    @property
    def audit_type_name(self):
        if self.audit_type:
            return self.audit_type.audit_type_name
        return "-"

    @property
    def audit_category_name(self):
        if self.audit_category:
            return self.audit_category.audit_category_name
        return "-"

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __repr__(self):
        return (
            f"<Audit "
            f"id={self.id}, "
            f"audit_no='{self.audit_no}', "
            f"title='{self.title}', "
            f"status='{self.status}'>"
        )