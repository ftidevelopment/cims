from app.extensions import db
from app.models.base_model import BaseModel


class KaizenDepartmentTarget(BaseModel):
    __tablename__ = "kaizen_department_targets"

    reporting_period_id = db.Column(
        db.Integer,
        db.ForeignKey("kaizen_reporting_periods.id"),
        nullable=False,
        index=True
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False,
        index=True
    )

    target_quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    reporting_period = db.relationship(
        "KaizenReportingPeriod",
        back_populates="department_targets"
    )

    department = db.relationship(
        "Department",
        back_populates="kaizen_department_targets"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "reporting_period_id",
            "department_id",
            name="uq_kaizen_department_target_period_department"
        ),
    )

    @property
    def reporting_period_name(self):
        if self.reporting_period:
            return self.reporting_period.period_name

        return ""


    @property
    def department_name(self):
        if self.department:
            return self.department.department_name

        return ""

    def __repr__(self):
        return (
            f"<KaizenDepartmentTarget "
            f"id={self.id}, "
            f"reporting_period_id={self.reporting_period_id}, "
            f"department_id={self.department_id}, "
            f"target_quantity={self.target_quantity}>"
        )