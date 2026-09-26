from app.extensions import db
from app.models.base_model import BaseModel


class IssueClarification(BaseModel):
    __tablename__ = "issue_clarifications"

    issue_id = db.Column(
        db.Integer,
        db.ForeignKey("issues.id"),
        nullable=False,
        index=True,
    )

    question = db.Column(
        db.Text,
        nullable=False,
    )

    response = db.Column(
        db.Text,
        nullable=True,
    )

    requested_by_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    responded_by_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=True,
        index=True,
    )

    requested_at = db.Column(
        db.DateTime,
        nullable=False,
    )

    responded_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="OPEN",
        index=True,
    )

    issue = db.relationship(
        "Issue",
        back_populates="clarifications",
    )

    requested_by = db.relationship(
        "Employee",
        foreign_keys=[requested_by_employee_id],
    )

    responded_by = db.relationship(
        "Employee",
        foreign_keys=[responded_by_employee_id],
    )

    def __repr__(self):
        return f"<IssueClarification {self.id}>"