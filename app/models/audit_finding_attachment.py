from app.extensions import db
from app.models.base_model import BaseModel


class AuditFindingAttachment(BaseModel):
    __tablename__ = "audit_finding_attachments"

    # ============================================================
    # Finding Reference
    # ============================================================

    audit_finding_id = db.Column(
        db.Integer,
        db.ForeignKey("audit_findings.id"),
        nullable=False
    )

    # ============================================================
    # File Information
    # ============================================================

    # Nama file asli yang di-upload oleh user
    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    # Nama file yang digunakan untuk penyimpanan di server
    # Dibuat unik agar tidak terjadi bentrok nama file
    stored_filename = db.Column(
        db.String(255),
        nullable=False
    )

    # Path file di server
    file_path = db.Column(
        db.String(500),
        nullable=False
    )

    # Extension file
    # Contoh: jpg, png, pdf, xlsx
    file_extension = db.Column(
        db.String(20),
        nullable=True
    )

    # MIME type
    # Contoh:
    # image/jpeg
    # image/png
    # application/pdf
    mime_type = db.Column(
        db.String(100),
        nullable=True
    )

    # Ukuran file dalam bytes
    file_size = db.Column(
        db.BigInteger,
        nullable=True
    )

    # ============================================================
    # Attachment Type
    # ============================================================

    # FINDING_EVIDENCE
    # CORRECTIVE_ACTION
    # VERIFICATION
    # OTHER
    attachment_type = db.Column(
        db.String(30),
        nullable=False,
        default="FINDING_EVIDENCE"
    )

    # ============================================================
    # Relationships
    # ============================================================

    audit_finding = db.relationship(
        "AuditFinding",
        back_populates="attachments",
        lazy="select"
    )

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self):
        return (
            f"<AuditFindingAttachment "
            f"id={self.id}, "
            f"audit_finding_id={self.audit_finding_id}, "
            f"original_filename='{self.original_filename}', "
            f"attachment_type='{self.attachment_type}'>"
        )