from app.extensions import db
from app.models.base_model import BaseModel


class NotificationRule(BaseModel):
    """
    Notification recipient configuration.
    """

    __tablename__ = "notification_rules"

    # ==========================================
    # Module
    # ==========================================

    module = db.Column(
        db.String(50),
        nullable=False,
    )

    # ==========================================
    # Event
    # ==========================================

    event = db.Column(
        db.String(50),
        nullable=False,
    )

    # ==========================================
    # Department
    # ==========================================

    department_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "departments.id"
        ),
        nullable=False,
    )

    # ==========================================
    # Employee
    # ==========================================

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "employees.id"
        ),
        nullable=False,
    )

    # ==========================================
    # Notification Channels
    # ==========================================

    email_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    line_enabled = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    # ==========================================
    # Relationships
    # ==========================================

    department = db.relationship(
        "Department",
        back_populates="notification_rules",
    )

    employee = db.relationship(
        "Employee",
        back_populates="notification_rules",
    )

    def __repr__(self):

        return (
            f"<NotificationRule "
            f"{self.module} - "
            f"{self.event} - "
            f"Employee:{self.employee_id}>"
        )