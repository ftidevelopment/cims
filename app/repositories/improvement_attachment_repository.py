from app.models.improvement_attachment import ImprovementAttachment
from app.repositories.base_repository import BaseRepository


class ImprovementAttachmentRepository(BaseRepository):

    def __init__(self):
        super().__init__(ImprovementAttachment)

    # --------------------------------------------------
    # Get Attachments by Improvement
    # --------------------------------------------------

    def find_by_improvement_id(self, improvement_id):
        return (
            self.model.query
            .filter_by(improvement_id=improvement_id)
            .order_by(
                ImprovementAttachment.sort_order.asc(),
                ImprovementAttachment.id.asc()
            )
            .all()
        )

    # --------------------------------------------------
    # Get Attachment by ID and Improvement
    # --------------------------------------------------

    def find_by_id_and_improvement(
        self,
        attachment_id,
        improvement_id
    ):
        return (
            self.model.query
            .filter_by(
                id=attachment_id,
                improvement_id=improvement_id
            )
            .first()
        )

    # --------------------------------------------------
    # Get Last Sort Order
    # --------------------------------------------------

    def get_last_sort_order(self, improvement_id):

        attachment = (
            self.model.query
            .filter_by(improvement_id=improvement_id)
            .order_by(
                ImprovementAttachment.sort_order.desc()
            )
            .first()
        )

        if not attachment:
            return 0

        return attachment.sort_order