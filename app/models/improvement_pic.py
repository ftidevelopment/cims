from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.base_model import BaseModel


class ImprovementPIC(BaseModel):

    __tablename__ = "improvement_pics"

    __table_args__ = (
    db.UniqueConstraint(
        "improvement_id",
        "employee_id",
        name="uq_improvement_pic",
    ),
)

    # ==================================================
    # Improvement
    # ==================================================

    improvement_id = db.Column(
        db.Integer,
        ForeignKey(
            "improvements.id"
        ),
        nullable=False,
        index=True,
    )

    # ==================================================
    # Employee
    # ==================================================

    employee_id = db.Column(
        db.Integer,
        ForeignKey(
            "employees.id"
        ),
        nullable=False,
        index=True,
    )

    # ==================================================
    # Leader
    # ==================================================

    is_leader = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    # ==================================================
    # Status
    # ==================================================

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ASSIGNED",
        index=True,
    )

    # ==================================================
    # Relationships
    # ==================================================

    improvement = relationship(
        "Improvement",
        back_populates="improvement_pics",
    )

    employee = relationship(
        "Employee",
        back_populates="improvement_pics",
    )

    # ==================================================
    # Representation
    # ==================================================

    def __repr__(self):

        return (
            f"<ImprovementPIC("
            f"improvement_id={self.improvement_id}, "
            f"employee_id={self.employee_id}, "
            f"is_leader={self.is_leader}, "
            f"status='{self.status}'"
            f")>"
        )