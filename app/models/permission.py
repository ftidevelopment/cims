from sqlalchemy.orm import relationship

from app.extensions import db

from app.models.base_model import BaseModel


class Permission(BaseModel):

    __tablename__ = "permissions"

    # ==========================================
    # Basic Information
    # ==========================================

    permission_code = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    permission_name = db.Column(
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

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        lazy="select",
    )

    # ==========================================
    # Representation
    # ==========================================

    def __repr__(self):

        return (
            f"<Permission("
            f"permission_code='{self.permission_code}', "
            f"permission_name='{self.permission_name}'"
            f")>"
        )