from app.extensions import db
from app.models.base_model import BaseModel


class KaizenAwardPeriod(BaseModel):
    __tablename__ = "kaizen_award_periods"

    # ==========================================================
    # BASIC INFORMATION
    # ==========================================================

    award_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    award_name = db.Column(
        db.String(100),
        nullable=False
    )

    # ==========================================================
    # AWARD PERIOD
    # ==========================================================

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    end_date = db.Column(
        db.Date,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================================================
    # RELATIONSHIP
    # ==========================================================

    kaizens = db.relationship(
        "Kaizen",
        back_populates="award_period",
        lazy="select"
    )

    judges = db.relationship(
        "KaizenAwardJudge",
        back_populates="award_period",
        lazy="select",
        cascade="all, delete-orphan"
    )

    scores = db.relationship(
        "KaizenAwardScore",
        back_populates="award_period",
        lazy="select",
        cascade="all, delete-orphan"
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Open",
        index=True
    )

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(self):
        return (
            f"<KaizenAwardPeriod("
            f"award_code='{self.award_code}', "
            f"award_name='{self.award_name}', "
            f"start_date='{self.start_date}', "
            f"end_date='{self.end_date}'"
            f")>"
        )