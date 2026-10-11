from app.extensions import db
from app.models.base_model import BaseModel


class AuditType(BaseModel):
    __tablename__ = "audit_types"

    audit_type_code = db.Column(
        db.String(10),
        unique=True,
        nullable=False
    )

    audit_type_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    audits = db.relationship(
        "Audit",
        back_populates="audit_type",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<AuditType "
            f"id={self.id}, "
            f"audit_type_code='{self.audit_type_code}', "
            f"audit_type_name='{self.audit_type_name}'>"
        )