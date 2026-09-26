from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.base_model import BaseModel
from app.core.choices.problem import PIC_STATUS


class ProblemPIC(BaseModel):
    __tablename__ = "problem_pics"

    problem_id = db.Column(
        db.Integer,
        ForeignKey("problems.id"),
        nullable=False,
        index=True
    )

    employee_id = db.Column(
        db.Integer,
        ForeignKey("employees.id"),
        nullable=False,
        index=True
    )

    is_leader = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default=PIC_STATUS[0][0]
    )

    # ==========================================
    # Relationship
    # ==========================================

    problem = relationship(
        "Problem",
        back_populates="problem_pics"
    )

    employee = relationship(
        "Employee",
        back_populates="problem_pics"
    )

    # ==========================================
    # Representation
    # ==========================================

    def __repr__(self):
        return (
            f"<ProblemPIC("
            f"problem_id={self.problem_id}, "
            f"employee_id={self.employee_id}, "
            f"status='{self.status}'"
            f")>"
        )