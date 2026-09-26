from app.extensions import db
from app.models.base_model import BaseModel


class KaizenCategory(BaseModel):
    """
    Master Kaizen Category.
    """

    __tablename__ = "kaizen_categories"

    kaizen_category_code = db.Column(
        db.String(10),
        unique=True,
        nullable=False,
    )

    kaizen_category_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    kaizens = db.relationship(
        "Kaizen",
        back_populates="kaizen_category",
        lazy="select"
    )

    def __repr__(self):
        return (
            f"<KaizenCategory "
            f"id={self.id}, "
            f"kaizen_category_code='{self.kaizen_category_code}', "
            f"kaizen_category_name='{self.kaizen_category_name}'>"
        )