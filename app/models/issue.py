from app.extensions import db
from app.models.base_model import BaseModel


class Issue(BaseModel):
    """
    CIMS Issue Management

    Workflow:

        OPEN
          ↓
        IN_PROGRESS
          ↓
        FINISH
          ↓
        CLOSE
    """

    __tablename__ = "issues"

    # ==========================================================
    # Issue Number
    # ==========================================================

    issue_no = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Issue Information
    # ==========================================================

    module = db.Column(
        db.String(30),
        nullable=False,
        index=True,
    )

    category = db.Column(
        db.String(30),
        nullable=False,
        index=True,
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="MEDIUM",
        index=True,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    # ==========================================================
    # Workflow Status
    # ==========================================================

    status = db.Column(
        db.String(20),
        nullable=False,
        default="OPEN",
        index=True,
    )

    # ==========================================================
    # Requestor
    # ==========================================================

    requestor_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    requestor = db.relationship(
        "Employee",
        foreign_keys=[requestor_employee_id],
    )

    # ==========================================================
    # Developer
    # ==========================================================

    developer_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=True,
        index=True,
    )

    developer = db.relationship(
        "Employee",
        foreign_keys=[developer_employee_id],
    )

    # ==========================================================
    # Workflow Dates
    # ==========================================================

    finished_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    closed_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    # ==========================================================
    # Attachments
    # ==========================================================

    attachments = db.relationship(
        "IssueAttachment",
        back_populates="issue",
        cascade="all, delete-orphan",
        order_by="IssueAttachment.sort_order",
        lazy="select",
    )

    clarifications = db.relationship(
        "IssueClarification",
        back_populates="issue",
        cascade="all, delete-orphan",
        order_by="IssueClarification.requested_at.asc()",
        lazy="select",
    )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self):
        return f"<Issue {self.issue_no}>"