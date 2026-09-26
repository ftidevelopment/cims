
from app.extensions import db
from app.models.base_model import BaseModel

class ProblemAttachment(BaseModel):

    __tablename__ = "problem_attachments"

    problem_id = db.Column(
        db.Integer,
        db.ForeignKey("problems.id"),
        nullable=False,
        index=True,
    )

    stored_name = db.Column(
        db.String(255),
        nullable=False,
    )

    original_name = db.Column(
        db.String(255),
        nullable=False,
    )

    extension = db.Column(
        db.String(20),
        nullable=False,
    )

    mime_type = db.Column(
        db.String(100),
    )

    file_size = db.Column(
        db.BigInteger,
        nullable=False,
        default=0,
    )

    sort_order = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    is_image = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    remarks = db.Column(
        db.String(255),
    )

    problem = db.relationship(
        "Problem",
        back_populates="attachments",
    )