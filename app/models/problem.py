from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.base_model import BaseModel
from app.core.choices.problem import (
    PROBLEM_PRIORITY,
    PROBLEM_STATUS
)


class Problem(BaseModel):
    __tablename__ = "problems"

    # ==================================================
    # Basic Information
    # ==================================================

    problem_no = db.Column(
        db.String(30),
        nullable=False,
        unique=True,
        index=True
    )

    problem_date = db.Column(
        db.Date,
        nullable=False
    )

    department_id = db.Column(
        db.Integer,
        ForeignKey("departments.id"),
        nullable=False,
        index=True
    )

    reporter_employee_id = db.Column(
        db.Integer,
        ForeignKey("employees.id"),
        nullable=False,
        index=True
    )

    monitor_employee_id = db.Column(
        db.Integer,
        ForeignKey("employees.id"),
        nullable=True,
        index=True
    )

    problem_category_id = db.Column(
        db.Integer,
        ForeignKey("problem_categories.id"),
        nullable=False,
        index=True
    )

    priority = db.Column(
        db.String(10),
        nullable=False,
        default=PROBLEM_PRIORITY[0][0]
    )

    problem_source = db.Column(
        db.String(30),
        nullable=True
    )

    problem_location = db.Column(
        db.String(100),
        nullable=True
    )

    # ==================================================
    # Problem Detail
    # ==================================================

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    problem_cause = db.Column(
        db.Text,
        nullable=True
    )

    problem_impact = db.Column(
        db.Text,
        nullable=True
    )

    # ==================================================
    # Loss Information
    # ==================================================

    loss_quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    loss_cost = db.Column(
        db.Numeric(18, 2),
        nullable=False,
        default=0
    )

    loss_time = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        comment="Minute"
    )

    # ==================================================
    # Attachment
    # ==================================================



    # ==================================================
    # Monitoring
    # ==================================================

    status = db.Column(
        db.String(20),
        nullable=False,
        default=PROBLEM_STATUS[0][0]
    )

    target_date = db.Column(
        db.Date,
        nullable=True
    )

    closed_date = db.Column(
        db.Date,
        nullable=True
    )

    # ==================================================
    # Relationship
    # ==================================================

    department = relationship(
        "Department",
        back_populates="problems"
    )

    problem_category = relationship(
        "ProblemCategory",
        back_populates="problems"
    )

    reporter = relationship(
        "Employee",
        foreign_keys=[reporter_employee_id]
    )

    monitor = relationship(
        "Employee",
        foreign_keys=[monitor_employee_id]
    )

    problem_pics = relationship(
        "ProblemPIC",
        back_populates="problem",
        cascade="all, delete-orphan"
    )

    improvements = relationship(
        "Improvement",
        back_populates="problem",
        cascade="all, delete-orphan"
    )

    attachments = relationship(
        "ProblemAttachment",
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="ProblemAttachment.sort_order",
        lazy="select"
    )

    kaizens = db.relationship(
        "Kaizen",
        back_populates="problem",
        lazy=True
    )

    # ==================================================
    # Representation
    # ==================================================

    def __repr__(self):
        return (
            f"<Problem("
            f"problem_no='{self.problem_no}', "
            f"title='{self.title}', "
            f"status='{self.status}'"
            f")>"
        )