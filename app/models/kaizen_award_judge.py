from app.extensions import db
from app.models.base_model import BaseModel


class KaizenAwardJudge(BaseModel):
    __tablename__ = "kaizen_award_judges"

    # ==========================================================
    # AWARD PERIOD
    # ==========================================================

    award_period_id = db.Column(
        db.Integer,
        db.ForeignKey("kaizen_award_periods.id"),
        nullable=False,
        index=True
    )

    # ==========================================================
    # JUDGE / EMPLOYEE
    # ==========================================================

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False,
        index=True
    )

    # ==========================================================
    # RELATIONSHIP
    # ==========================================================

    award_period = db.relationship(
        "KaizenAwardPeriod",
        back_populates="judges"
    )

    employee = db.relationship(
        "Employee",
        foreign_keys=[employee_id]
    )

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(self):
        return (
            f"<KaizenAwardJudge("
            f"award_period_id={self.award_period_id}, "
            f"employee_id={self.employee_id}"
            f")>"
        )