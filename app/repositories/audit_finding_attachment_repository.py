from app.models.audit_finding_attachment import AuditFindingAttachment
from app.repositories.base_repository import BaseRepository


class AuditFindingAttachmentRepository(BaseRepository):
    model = AuditFindingAttachment

    searchable_fields = [
        AuditFindingAttachment.original_filename,
        AuditFindingAttachment.description,
        AuditFindingAttachment.attachment_type,
        AuditFindingAttachment.mime_type,
    ]

    sortable_fields = {
        "original_filename": AuditFindingAttachment.original_filename,
        "attachment_type": AuditFindingAttachment.attachment_type,
        "file_size": AuditFindingAttachment.file_size,
        "created_at": AuditFindingAttachment.created_at,
    }

    def __init__(self):
        super().__init__(AuditFindingAttachment)

    def get_by_finding(self, audit_finding_id: int):
        return (
            self.model.query
            .filter_by(
                audit_finding_id=audit_finding_id,
                is_active=True
            )
            .order_by(self.model.created_at.asc())
            .all()
        )

    def get_by_type(
        self,
        audit_finding_id: int,
        attachment_type: str
    ):
        return (
            self.model.query
            .filter_by(
                audit_finding_id=audit_finding_id,
                attachment_type=attachment_type,
                is_active=True
            )
            .order_by(self.model.created_at.asc())
            .all()
        )

    def get_by_id_for_finding(
        self,
        attachment_id: int,
        audit_finding_id: int
    ):
        return (
            self.model.query
            .filter_by(
                id=attachment_id,
                audit_finding_id=audit_finding_id,
                is_active=True
            )
            .first()
        )

    def hard_delete(self, attachment):
        from app.extensions import db

        db.session.delete(attachment)