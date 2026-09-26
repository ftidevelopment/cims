from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.base_model import BaseModel


class ImprovementAttachment(BaseModel):
    """
    Store attachment information for an Improvement.

    Supported file types will be validated in the Service layer.
    """

    __tablename__ = "improvement_attachments"

    # --------------------------------------------------
    # Relationship
    # --------------------------------------------------

    improvement_id = db.Column(
        db.Integer,
        ForeignKey("improvements.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------
    # File Information
    # --------------------------------------------------

    file_name = db.Column(
        db.String(255),
        nullable=False
    )

    stored_name = db.Column(
        db.String(255),
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=False
    )

    file_type = db.Column(
        db.String(20),
        nullable=False
    )

    file_size = db.Column(
        db.BigInteger,
        nullable=True
    )

    # --------------------------------------------------
    # Attachment Information
    # --------------------------------------------------

    description = db.Column(
        db.String(500),
        nullable=True
    )

    sort_order = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # --------------------------------------------------
    # Relationship
    # --------------------------------------------------

    improvement = relationship(
        "Improvement",
        back_populates="attachments"
    )

    # --------------------------------------------------
    # Representation
    # --------------------------------------------------

    def __repr__(self):
        return (
            f"<ImprovementAttachment("
            f"id={self.id}, "
            f"improvement_id={self.improvement_id}, "
            f"file_name='{self.file_name}'"
            f")>"
        )