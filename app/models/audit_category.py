from app.extensions import db
from app.models.base_model import BaseModel


class AuditCategory(BaseModel):
    """
    Master Audit / Patrol Category.
    """

    __tablename__ = "audit_categories"

    audit_category_code = db.Column(
        db.String(10),
        unique=True,
        nullable=False,
    )

    audit_category_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    audits = db.relationship(
        "Audit",
        back_populates="audit_category",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<AuditCategory "
            f"id={self.id}, "
            f"audit_category_code='{self.audit_category_code}', "
            f"audit_category_name='{self.audit_category_name}'>"
        )