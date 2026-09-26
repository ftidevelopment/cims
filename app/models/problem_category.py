from app.extensions import db
from app.models.base_model import BaseModel


class ProblemCategory(BaseModel):
    """
    Master Problem Category.
    """

    __tablename__ = "problem_categories"

    problem_category_code = db.Column(
        db.String(10),
        unique=True,
        nullable=False,
    )

    problem_category_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )
    problems = db.relationship(
        "Problem",
        back_populates="problem_category",
        lazy="select"
    )

    def __repr__(self):
        return (
            f"<ProblemCategory "
            f"id={self.id}, "
            f"problem_category_code='{self.problem_category_code}', "
            f"problem_category_name='{self.problem_category_name}'>"
        )