from app.extensions import db
from app.models.base_model import BaseModel
from app.core.choices.kaizen import KAIZEN_STATUS

class Kaizen(BaseModel):
    __tablename__ = "kaizens"

    # ==========================================================
    # BASIC INFORMATION
    # ==========================================================

    kaizen_no = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    kaizen_category_id = db.Column(
        db.Integer,
        db.ForeignKey("kaizen_categories.id"),
        nullable=True,
        index=True
    )

    # ==========================================================
    # RELATION TO PROBLEM
    # Optional
    # Direct Kaizen is allowed
    # ==========================================================

    problem_id = db.Column(
        db.Integer,
        db.ForeignKey("problems.id"),
        nullable=True,
        index=True
    )

    # ==========================================================
    # RELATION TO IMPROVEMENT
    # Optional
    # Direct Kaizen is allowed
    # ==========================================================

    improvement_id = db.Column(
        db.Integer,
        db.ForeignKey("improvements.id"),
        nullable=True,
        index=True
    )

    # ==========================================================
    # PIC / CREATOR
    # ==========================================================

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False,
        index=True
    )

    # ==========================================================
    # DEPARTMENT
    # ==========================================================

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False,
        index=True
    )

    # ==========================================================
    # BEFORE CONDITION
    # ==========================================================

    before_condition = db.Column(
        db.Text,
        nullable=True
    )

    before_value = db.Column(
        db.Numeric(15, 2),
        nullable=True
    )

    before_unit = db.Column(
        db.String(50),
        nullable=True
    )

    loss_before = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================================================
    # AFTER CONDITION
    # ==========================================================

    after_condition = db.Column(
        db.Text,
        nullable=True
    )

    after_value = db.Column(
        db.Numeric(15, 2),
        nullable=True
    )

    after_unit = db.Column(
        db.String(50),
        nullable=True
    )

    benefit = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================================================
    # COST SAVING
    # ==========================================================

    cost_saving = db.Column(
        db.Numeric(15, 2),
        nullable=True
    )

    # ==========================================================
    # IMPLEMENTATION
    # ==========================================================

    implementation_date = db.Column(
        db.Date,
        nullable=True
    )

    # ==========================================================
    # WORKFLOW STATUS
    #
    # Draft
    # Proposal
    # Approved
    # Rejected
    # Implemented
    # ==========================================================

    status = db.Column(
        db.String(30),
        nullable=False,
        default=KAIZEN_STATUS[0][0],
        index=True
    )

    # ==========================================================
    # APPROVAL
    # ==========================================================

    approved_by_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=True,
        index=True
    )

    approved_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ==========================================================
    # REJECTION
    # ==========================================================

    rejected_by_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=True,
        index=True
    )

    rejected_at = db.Column(
        db.DateTime,
        nullable=True
    )

    rejection_reason = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================================================
    # RELATIONSHIP
    # ==========================================================

    # ----------------------------------------------------------
    # Problem
    # ----------------------------------------------------------

    problem = db.relationship(
        "Problem",
        back_populates="kaizens"
    )

    # ----------------------------------------------------------
    # Improvement
    # ----------------------------------------------------------

    improvement = db.relationship(
        "Improvement",
        back_populates="kaizens"
    )

    # ----------------------------------------------------------
    # Kaizen Creator / PIC
    # ----------------------------------------------------------

    employee = db.relationship(
        "Employee",
        foreign_keys=[employee_id]
    )

    # ----------------------------------------------------------
    # Department
    # ----------------------------------------------------------

    department = db.relationship(
        "Department",
        foreign_keys=[department_id]
    )

    # ----------------------------------------------------------
    # Approved By
    # ----------------------------------------------------------

    approved_by = db.relationship(
        "Employee",
        foreign_keys=[approved_by_employee_id]
    )

    # ----------------------------------------------------------
    # Rejected By
    # ----------------------------------------------------------

    rejected_by = db.relationship(
        "Employee",
        foreign_keys=[rejected_by_employee_id]
    )

    # ----------------------------------------------------------
    # Attachments
    # ----------------------------------------------------------

    attachments = db.relationship(
        "KaizenAttachment",
        back_populates="kaizen",
        cascade="all, delete-orphan",
        order_by="KaizenAttachment.sort_order",
        lazy="select"
    )

    kaizen_category = db.relationship(
        "KaizenCategory",
        back_populates="kaizens"
    )

    award_period_id = db.Column(
        db.Integer,
        db.ForeignKey("kaizen_award_periods.id"),
        nullable=True,
        index=True
    )

    award_period = db.relationship(
        "KaizenAwardPeriod",
        back_populates="kaizens"
    )

    award_scores = db.relationship(
        "KaizenAwardScore",
        back_populates="kaizen",
        lazy="select",
        cascade="all, delete-orphan"
    )

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(self):
        return (
            f"<Kaizen("
            f"kaizen_no='{self.kaizen_no}', "
            f"title='{self.title}', "
            f"status='{self.status}'"
            f")>"
        )