from datetime import datetime

from app.extensions import db


class BaseModel(db.Model):
    """
    Base model untuk seluruh tabel di CIMS.
    """

    __abstract__ = True

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    created_by = db.Column(
        db.String(50),
        nullable=True,
    )

    updated_by = db.Column(
        db.String(50),
        nullable=True,
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    version = db.Column(
        db.Integer,
        default=1,
        nullable=False,
    )