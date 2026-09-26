from sqlalchemy.orm import relationship

from app.extensions import db

from app.models.base_model import BaseModel


class Role(BaseModel):

    __tablename__ = "roles"

    # ==========================================
    # Basic Information
    # ==========================================

    role_code = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    role_name = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    description = db.Column(
        db.String(255),
        nullable=True,
    )

    # ==========================================
    # Relationship
    # ==========================================

    users = relationship(
        "User",
        back_populates="role",
        lazy="select",
    )

    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        lazy="select",
    )

    # ==========================================
    # Representation
    # ==========================================

    def __repr__(self):

        return (
            f"<Role("
            f"role_code='{self.role_code}', "
            f"role_name='{self.role_name}'"
            f")>"
        )