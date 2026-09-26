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