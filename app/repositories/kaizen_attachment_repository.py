from app.models.kaizen_attachment import KaizenAttachment
from app.repositories.base_repository import BaseRepository


class KaizenAttachmentRepository(BaseRepository):

    def __init__(self):
        super().__init__(KaizenAttachment)

    # --------------------------------------------------
    # Get Attachments by Kaizen
    # --------------------------------------------------

    def find_by_kaizen_id(self, kaizen_id):
        return (
            self.model.query
            .filter_by(kaizen_id=kaizen_id)
            .order_by(
                KaizenAttachment.sort_order.asc(),
                KaizenAttachment.id.asc()
            )
            .all()
        )

    # --------------------------------------------------
    # Get Attachments by Kaizen and Type
    # --------------------------------------------------

    def find_by_kaizen_id_and_type(
        self,
        kaizen_id,
        attachment_type
    ):
        return (
            self.model.query
            .filter_by(
                kaizen_id=kaizen_id,
                attachment_type=attachment_type
            )
            .order_by(
                KaizenAttachment.sort_order.asc(),
                KaizenAttachment.id.asc()
            )
            .all()
        )

    # --------------------------------------------------
    # Get Attachment by ID and Kaizen
    # --------------------------------------------------

    def find_by_id_and_kaizen(
        self,
        attachment_id,
        kaizen_id
    ):
        return (
            self.model.query
            .filter_by(
                id=attachment_id,
                kaizen_id=kaizen_id
            )
            .first()
        )

    # --------------------------------------------------
    # Get Last Sort Order
    # --------------------------------------------------

    def get_last_sort_order(self, kaizen_id):

        attachment = (
            self.model.query
            .filter_by(kaizen_id=kaizen_id)
            .order_by(
                KaizenAttachment.sort_order.desc()
            )
            .first()
        )

        if not attachment:
            return 0

        return attachment.sort_order