from app.extensions import db
from app.models.base_model import BaseModel


class NumberSequence(BaseModel):
    """
    Store running number sequence for CIMS documents.

    Example:
        problem      -> 125
        improvement  -> 27
        kaizen       -> 58
    """

    __tablename__ = "number_sequences"

    sequence_name = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
        index=True
    )

    current_number = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    def __repr__(self):
        return (
            f"<NumberSequence("
            f"sequence_name='{self.sequence_name}', "
            f"current_number={self.current_number}"
            f")>"
        )