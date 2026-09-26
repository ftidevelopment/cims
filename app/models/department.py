from app.extensions import db
from app.models.base_model import BaseModel


class Department(BaseModel):
    """
    Master Data Department
    """

    __tablename__ = "departments"

    department_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
    )

    department_name = db.Column(
        db.String(100),
        nullable=False,
    )

    description = db.Column(
        db.String(255),
        nullable=True,
    )

    employees = db.relationship(
        "Employee",
        back_populates="department",
        lazy=True,
    )

    problems = db.relationship(
        "Problem",
        back_populates="department",
        lazy="select"
    )

    kaizen_department_targets = db.relationship(
        "KaizenDepartmentTarget",
        back_populates="department",
        lazy="select"
    )

    problem_assignment_authorities = db.relationship(
        "ProblemAssignmentAuthority",
        back_populates="department",
        cascade="all, delete-orphan",
    )

    improvement_assignment_authorities = db.relationship(
        "ImprovementAssignmentAuthority",
        back_populates="department",
        lazy="select",
    )

    improvement_approval_authorities = db.relationship(
        "ImprovementApprovalAuthority",
        back_populates="department",
        lazy="select",
    )

    # ==========================================================
    # Kaizen Approval Authorities
    # ==========================================================

    kaizen_approval_authorities = db.relationship(
        "KaizenApprovalAuthority",
        foreign_keys="KaizenApprovalAuthority.department_id",
        back_populates="department",
        cascade="all, delete-orphan",
    )

    notification_rules = db.relationship(
        "NotificationRule",
        back_populates="department",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Department "
            f"{self.department_code} - "
            f"{self.department_name}>"
        )