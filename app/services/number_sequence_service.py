from app.extensions import db
from app.models.number_sequence import NumberSequence
from app.repositories.number_sequence_repository import (
    NumberSequenceRepository
)


class NumberSequenceService:
    """
    Service for generating sequential document numbers.

    This service can be used by:
        - Problem
        - Improvement
        - Kaizen
        - Other CIMS documents
    """

    def __init__(self):
        self.repository = NumberSequenceRepository()

    def get_next_number(
        self,
        sequence_name,
        prefix,
        digit=3
    ):
        """
        Generate the next document number.

        Example:
            sequence_name = "improvement"
            prefix = "IMP"
            digit = 3

            Result:
                IMP001
                IMP002
                IMP003
        """

        # ==========================================
        # Get sequence with database lock
        # ==========================================
        sequence = self.repository.get_for_update(
            sequence_name
        )

        # ==========================================
        # Sequence does not exist
        # ==========================================
        if not sequence:

            sequence = NumberSequence(
                sequence_name=sequence_name,
                current_number=1
            )

            self.repository.create(sequence)

            db.session.flush()

            return f"{prefix}{1:0{digit}d}"

        # ==========================================
        # Increment sequence
        # ==========================================
        sequence.current_number += 1

        db.session.flush()

        return (
            f"{prefix}"
            f"{sequence.current_number:0{digit}d}"
        )