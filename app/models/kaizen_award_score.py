from app.extensions import db
from app.models.base_model import BaseModel


class KaizenAwardScore(BaseModel):
    __tablename__ = "kaizen_award_scores"

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
    # KAIZEN
    # ==========================================================

    kaizen_id = db.Column(
        db.Integer,
        db.ForeignKey("kaizens.id"),
        nullable=False,
        index=True
    )

    # ==========================================================
    # JUDGE
    # ==========================================================

    judge_employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False,
        index=True
    )

    # ==========================================================
    # SCORE
    # ==========================================================

    score = db.Column(
        db.Numeric(5, 2),
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=True
    )

    scored_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ==========================================================
    # UNIQUE CONSTRAINT
    # ==========================================================

    __table_args__ = (
        db.UniqueConstraint(
            "award_period_id",
            "kaizen_id",
            "judge_employee_id",
            name="uq_kaizen_award_score"
        ),
    )

    # ==========================================================
    # RELATIONSHIP
    # ==========================================================

    award_period = db.relationship(
        "KaizenAwardPeriod",
        back_populates="scores"
    )

    kaizen = db.relationship(
        "Kaizen",
        back_populates="award_scores"
    )

    judge_employee = db.relationship(
        "Employee",
        foreign_keys=[judge_employee_id]
    )

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(self):
        return (
            f"<KaizenAwardScore("
            f"award_period_id={self.award_period_id}, "
            f"kaizen_id={self.kaizen_id}, "
            f"judge_employee_id={self.judge_employee_id}, "
            f"score={self.score}"
            f")>"
        )