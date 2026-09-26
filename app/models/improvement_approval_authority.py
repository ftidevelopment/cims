from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.base_model import BaseModel


class ImprovementApprovalAuthority(BaseModel):

    __tablename__ = "improvement_approval_authorities"

    # ==================================================
    # Unique Constraint
    # ==================================================

    __table_args__ = (
        db.UniqueConstraint(
            "department_id",
            "employee_id",
            name="uq_improvement_approval_authority",
        ),
    )

    # ==================================================
    # Department
    # ==================================================

    department_id = db.Column(
        db.Integer,
        ForeignKey(
            "departments.id"
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
    # Relationships
    # ==================================================

    department = relationship(
        "Department",
        back_populates=(
            "improvement_approval_authorities"
        ),
    )

    employee = relationship(
        "Employee",
        back_populates=(
            "improvement_approval_authorities"
        ),
    )

    # ==================================================
    # Representation
    # ==================================================

    def __repr__(self):

        return (
            f"<ImprovementApprovalAuthority("
            f"department_id={self.department_id}, "
            f"employee_id={self.employee_id}"
            f")>"
        )