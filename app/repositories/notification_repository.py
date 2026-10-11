from app.models.notification_log import NotificationLog
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    """
    Repository for notification log operations.
    """

    def __init__(self):
        super().__init__(
            model=NotificationLog
        )

    def exists_sent_notification_by_subject(
        self,
        event,
        subject,
    ):
        return (
            self.model.query
            .filter(
                self.model.event == event,
                self.model.subject == subject,
                self.model.status == "SENT",
            )
            .first()
            is not None
        )