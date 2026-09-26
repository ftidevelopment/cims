from app.extensions import db
from app.models.base_model import BaseModel


class IssueAttachment(BaseModel):
    """
    Attachment for CIMS Issue.
    """

    __tablename__ = "issue_attachments"

    # ==========================================================
    # Relationship
    # ==========================================================

    issue_id = db.Column(
        db.Integer,
        db.ForeignKey("issues.id"),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # File Information
    # ==========================================================

    file_name = db.Column(
        db.String(255),
        nullable=False,
    )

    stored_name = db.Column(
        db.String(255),
        nullable=False,
    )

    file_path = db.Column(
        db.String(500),
        nullable=False,
    )

    file_type = db.Column(
        db.String(20),
        nullable=False,
    )

    file_size = db.Column(
        db.BigInteger,
        nullable=True,
    )

    description = db.Column(
        db.String(500),
        nullable=True,
    )

    sort_order = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    # ==========================================================
    # Relationship
    # ==========================================================

    issue = db.relationship(
        "Issue",
        back_populates="attachments",
    )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self):
        return f"<IssueAttachment {self.file_name}>"