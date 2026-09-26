from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.base_model import BaseModel


class ProblemAssignmentAuthority(BaseModel):

    __tablename__ = "problem_assignment_authorities"

    # ==================================================
    # Table Constraints
    # ==================================================

    __table_args__ = (
        UniqueConstraint(
            "department_id",
            "employee_id",
            name="uq_problem_assignment_authority",
        ),
    )

    # ==================================================
    # Department
    # ==================================================

    department_id = db.Column(
        db.Integer,
        ForeignKey("departments.id"),
        nullable=False,
        index=True,
    )

    # ==================================================
    # Employee
    # ==================================================

    employee_id = db.Column(
        db.Integer,
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    # ==================================================
    # Relationships
    # ==================================================

    department = relationship(
        "Department",
        back_populates="problem_assignment_authorities",
        lazy="select",
    )

    employee = relationship(
        "Employee",
        back_populates="problem_assignment_authorities",
        lazy="select",
    )

    # ==================================================
    # Representation
    # ==================================================

    def __repr__(self):

        return (
            f"<ProblemAssignmentAuthority("
            f"department_id={self.department_id}, "
            f"employee_id={self.employee_id}"
            f")>"
        )