from app.extensions import db
from app.models.base_model import BaseModel


class Employee(BaseModel):
    """
    Master Data Employee
    """

    __tablename__ = "employees"

    nik = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
    )

    full_name = db.Column(
        db.String(100),
        nullable=False,
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False,
    )


    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    phone_number = db.Column(
        db.String(20),
        nullable=True,
    )

    telegram_chat_id = db.Column(
        db.String(50),
        nullable=True,
    )


    line_user_id = db.Column(
        db.String(100),
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ACTIVE",
    )

    department = db.relationship(
        "Department",
        back_populates="employees",
    )

    reported_problems = db.relationship(
        "Problem",
        foreign_keys="Problem.reporter_employee_id",
        back_populates="reporter",
        lazy="select"
    )

    monitored_problems = db.relationship(
        "Problem",
        foreign_keys="Problem.monitor_employee_id",
        back_populates="monitor",
        lazy="select"
    )

    problem_pics = db.relationship(
        "ProblemPIC",
        back_populates="employee",
        lazy="select"
    )

    problem_assignment_authorities = db.relationship(
        "ProblemAssignmentAuthority",
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    notification_rules = db.relationship(
        "NotificationRule",
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    improvement_assignment_authorities = db.relationship(
        "ImprovementAssignmentAuthority",
        back_populates="employee",
        lazy="select",
    )

    improvement_approval_authorities = db.relationship(
        "ImprovementApprovalAuthority",
        back_populates="employee",
        lazy="select",
    )

    improvement_pics = db.relationship(
        "ImprovementPIC",
        back_populates="employee",
        lazy="select",
    )

    # ==========================================================
    # Kaizen Approval Authorities
    # ==========================================================

    kaizen_approval_authorities = db.relationship(
        "KaizenApprovalAuthority",
        foreign_keys="KaizenApprovalAuthority.employee_id",
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    issues_requested = db.relationship(
        "Issue",
        foreign_keys="Issue.requestor_employee_id",
        back_populates="requestor",
        lazy="select",
    )

    issues_developed = db.relationship(
        "Issue",
        foreign_keys="Issue.developer_employee_id",
        back_populates="developer",
        lazy="select",
    )

    issue_clarifications_requested = db.relationship(
        "IssueClarification",
        foreign_keys="IssueClarification.requested_by_employee_id",
        lazy="select",
    )

    issue_clarifications_responded = db.relationship(
        "IssueClarification",
        foreign_keys="IssueClarification.responded_by_employee_id",
        lazy="select",
    )
  
    def __repr__(self):
        return f"<Employee {self.nik} - {self.full_name}>"