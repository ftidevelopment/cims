from app.extensions import db
from app.models.base_model import BaseModel


class KaizenApprovalAuthority(BaseModel):

    __tablename__ = "kaizen_approval_authorities"

    __table_args__ = (
        db.UniqueConstraint(
            "department_id",
            "employee_id",
            name="uq_kaizen_approval_authority_department_employee",
        ),
    )

    # ==========================================================
    # Department
    # ==========================================================

    department_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "departments.id"
        ),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Employee
    # ==========================================================

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "employees.id"
        ),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    department = db.relationship(
        "Department",
        foreign_keys=[
            department_id
        ],
        back_populates="kaizen_approval_authorities",
    )

    employee = db.relationship(
        "Employee",
        foreign_keys=[
            employee_id
        ],
        back_populates="kaizen_approval_authorities",
    )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self):

        return (
            f"<KaizenApprovalAuthority("
            f"department_id="
            f"{self.department_id}, "
            f"employee_id="
            f"{self.employee_id}, "
            f"is_active="
            f"{self.is_active}"
            f")>"
        )