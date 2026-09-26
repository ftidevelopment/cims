from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.base_model import BaseModel


class Improvement(BaseModel):

    __tablename__ = "improvements"

    # ==================================================
    # Relationship to Problem
    # ==================================================

    problem_id = db.Column(
        db.Integer,
        ForeignKey(
            "problems.id"
        ),
        nullable=False,
        index=True,
    )

    # ==================================================
    # Basic Information
    # ==================================================

    improvement_no = db.Column(
        db.String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    # ==================================================
    # Analysis
    # ==================================================

    root_cause = db.Column(
        db.Text,
        nullable=True,
    )

    # ==================================================
    # Improvement Action
    # ==================================================

    improvement_plan = db.Column(
        db.Text,
        nullable=True,
    )

    implementation_result = db.Column(
        db.Text,
        nullable=True,
    )

    # ==================================================
    # Cost & Benefit
    # ==================================================

    improvement_cost = db.Column(
        db.Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Improvement implementation cost",
    )

    estimated_time_saving = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        comment="Estimated time saving in minutes",
    )

    estimated_cost_saving = db.Column(
        db.Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Estimated cost saving",
    )

    estimated_benefit = db.Column(
        db.Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Estimated total benefit in monetary value",
    )

    # ==================================================
    # Ownership
    # ==================================================

    owner_employee_id = db.Column(
        db.Integer,
        ForeignKey(
            "employees.id"
        ),
        nullable=True,
        index=True,
    )

    # ==================================================
    # Verification
    # ==================================================

    verification_result = db.Column(
        db.Text,
        nullable=True,
    )

    # ==================================================
    # Approval
    # ==================================================

    approved_by_employee_id = db.Column(
        db.Integer,
        ForeignKey(
            "employees.id"
        ),
        nullable=True,
        index=True,
    )

    approved_date = db.Column(
        db.Date,
        nullable=True,
    )

    # ==================================================
    # Relationships
    # ==================================================

    # --------------------------------------------------
    # Problem
    # --------------------------------------------------

    problem = relationship(
        "Problem",
        back_populates="improvements",
    )

    # --------------------------------------------------
    # Owner / PIC
    # --------------------------------------------------

    owner_employee  = relationship(
        "Employee",
        foreign_keys=[
            owner_employee_id
        ],
    )

    # --------------------------------------------------
    # Approver
    # --------------------------------------------------

    approved_by = relationship(
        "Employee",
        foreign_keys=[
            approved_by_employee_id
        ],
    )

    improvement_pics = relationship(
        "ImprovementPIC",
        back_populates="improvement",
        cascade="all, delete-orphan",
        order_by="ImprovementPIC.is_leader.desc(), ImprovementPIC.id.asc()",
        lazy="select",
    )

    # --------------------------------------------------
    # Attachments
    # --------------------------------------------------

    attachments = relationship(
        "ImprovementAttachment",
        back_populates="improvement",
        cascade="all, delete-orphan",
        order_by=(
            "ImprovementAttachment.sort_order"
        ),
        lazy="select",
    )

    # --------------------------------------------------
    # Kaizen
    # --------------------------------------------------

    kaizens = relationship(
        "Kaizen",
        back_populates="improvement",
        lazy=True,
    )

    # ==================================================
    # Representation
    # ==================================================

    def __repr__(self):

        return (
            f"<Improvement("
            f"improvement_no="
            f"'{self.improvement_no}', "
            f"title="
            f"'{self.title}', "
            f"problem_id="
            f"{self.problem_id}, "
            f"owner_employee_id="
            f"{self.owner_employee_id}"
            f")>"
        )