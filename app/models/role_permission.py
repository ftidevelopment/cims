from sqlalchemy.orm import relationship

from app.extensions import db

from app.models.base_model import BaseModel


class RolePermission(BaseModel):

    __tablename__ = "role_permissions"

    # ==========================================
    # Foreign Keys
    # ==========================================

    role_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "roles.id"
        ),
        nullable=False,
        index=True,
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "permissions.id"
        ),
        nullable=False,
        index=True,
    )

    # ==========================================
    # Relationships
    # ==========================================

    role = relationship(
        "Role",
        back_populates="role_permissions",
    )

    permission = relationship(
        "Permission",
        back_populates="role_permissions",
    )

    # ==========================================
    # Representation
    # ==========================================

    def __repr__(self):

        return (
            f"<RolePermission("
            f"role_id={self.role_id}, "
            f"permission_id={self.permission_id}"
            f")>"
        )