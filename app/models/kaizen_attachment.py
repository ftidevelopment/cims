from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.base_model import BaseModel


class KaizenAttachment(BaseModel):
    """
    Store attachment information for a Kaizen.

    Supported file types will be validated in the Service layer.
    """

    __tablename__ = "kaizen_attachments"

    # --------------------------------------------------
    # Relationship
    # --------------------------------------------------

    kaizen_id = db.Column(
        db.Integer,
        ForeignKey("kaizens.id"),
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

    attachment_type = db.Column(
        db.String(20),
        nullable=False,
        default="GENERAL",
        index=True
    )

    sort_order = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # --------------------------------------------------
    # Relationship
    # --------------------------------------------------

    kaizen = relationship(
        "Kaizen",
        back_populates="attachments"
    )

    # --------------------------------------------------
    # Representation
    # --------------------------------------------------

    def __repr__(self):
        return (
            f"<KaizenAttachment("
            f"id={self.id}, "
            f"kaizen_id={self.kaizen_id}, "
            f"file_name='{self.file_name}'"
            f")>"
        )