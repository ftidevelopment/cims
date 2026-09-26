from app.extensions import db
from app.models.base_model import BaseModel


class KaizenReportingPeriod(BaseModel):
    """
    Master periode reporting Kaizen.

    Periode ditentukan berdasarkan rentang tanggal,
    sehingga dapat digunakan untuk semester maupun
    periode monitoring lainnya.
    """

    __tablename__ = "kaizen_reporting_periods"

    period_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    period_name = db.Column(
        db.String(100),
        nullable=False
    )

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

    department_targets = db.relationship(
        "KaizenDepartmentTarget",
        back_populates="reporting_period",
        lazy="select"
    )

    def __repr__(self):
        return (
            f"<KaizenReportingPeriod "
            f"id={self.id}, "
            f"period_code='{self.period_code}', "
            f"period_name='{self.period_name}', "
            f"start_date='{self.start_date}', "
            f"end_date='{self.end_date}'>"
        )