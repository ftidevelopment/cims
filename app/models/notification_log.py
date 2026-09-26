from app.extensions import db
from app.models.base_model import BaseModel


class NotificationLog(BaseModel):
    """
    Notification delivery log.
    """

    __tablename__ = "notification_logs"

    event = db.Column(
        db.String(50),
        nullable=False,
    )

    channel = db.Column(
        db.String(20),
        nullable=False,
    )

    recipient = db.Column(
        db.String(255),
        nullable=False,
    )

    subject = db.Column(
        db.String(255),
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
    )

    error_message = db.Column(
        db.Text,
        nullable=True,
    )

    sent_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    def __repr__(self):
        return (
            f"<NotificationLog "
            f"{self.event} - "
            f"{self.channel} - "
            f"{self.status}>"
        )