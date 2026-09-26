from app.models.issue_attachment import IssueAttachment
from app.repositories.base_repository import BaseRepository
from app.extensions import db


class IssueAttachmentRepository(BaseRepository):
    """
    Repository for Issue Attachment.

    Handles database operations for attachments
    belonging to an Issue.
    """

    model = IssueAttachment

    searchable_fields = [
        IssueAttachment.file_name,
        IssueAttachment.file_type,
        IssueAttachment.description,
    ]

    sortable_fields = {
        "file_name": IssueAttachment.file_name,
        "file_type": IssueAttachment.file_type,
        "file_size": IssueAttachment.file_size,
        "sort_order": IssueAttachment.sort_order,
        "created_at": IssueAttachment.created_at,
    }

    def __init__(self):
        super().__init__(IssueAttachment)

    # ==========================================================
    # GET BY ISSUE
    # ==========================================================

    def get_by_issue(self, issue_id):
        """
        Get all active attachments belonging to an Issue.
        """

        return (
            self.model.query
            .filter(
                self.model.issue_id == issue_id,
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.sort_order.asc(),
                self.model.created_at.asc(),
            )
            .all()
        )

    # ==========================================================
    # GET BY FILE NAME
    # ==========================================================

    def get_by_file_name(
        self,
        issue_id,
        file_name,
    ):
        """
        Get an attachment by Issue and original file name.
        """

        return (
            self.model.query
            .filter(
                self.model.issue_id == issue_id,
                self.model.file_name == file_name,
                self.model.is_active.is_(True),
            )
            .first()
        )

    # ==========================================================
    # GET NEXT SORT ORDER
    # ==========================================================

    def get_next_sort_order(self, issue_id):
        """
        Get the next sort order for a new attachment.
        """

        last_attachment = (
            self.model.query
            .filter(
                self.model.issue_id == issue_id,
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.sort_order.desc()
            )
            .first()
        )

        if not last_attachment:
            return 1

        return last_attachment.sort_order + 1

    # ==========================================================
    # HARD DELETE
    # ==========================================================

    def hard_delete(self, attachment):
        """
        Permanently delete attachment record from database.
        """

        db.session.delete(attachment)