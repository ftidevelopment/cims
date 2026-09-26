from app.models.number_sequence import NumberSequence
from app.repositories.base_repository import BaseRepository


class NumberSequenceRepository(BaseRepository):

    def __init__(self):
        super().__init__(NumberSequence)

    def get_for_update(self, sequence_name):
        """
        Get sequence row with database row-level lock.

        This is used when generating document numbers
        to prevent duplicate numbers during concurrent requests.
        """

        return (
            self.model.query
            .filter_by(sequence_name=sequence_name)
            .with_for_update()
            .first()
        )