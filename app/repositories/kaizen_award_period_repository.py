from app.models.kaizen_award_period import KaizenAwardPeriod
from app.repositories.base_repository import BaseRepository


class KaizenAwardPeriodRepository(BaseRepository):

    model = KaizenAwardPeriod

    searchable_fields = [
        KaizenAwardPeriod.award_code,
        KaizenAwardPeriod.award_name,
        KaizenAwardPeriod.description,
    ]

    sortable_fields = {
        "award_code": KaizenAwardPeriod.award_code,
        "award_name": KaizenAwardPeriod.award_name,
        "start_date": KaizenAwardPeriod.start_date,
        "end_date": KaizenAwardPeriod.end_date,
        "created_at": KaizenAwardPeriod.created_at,
    }

    def __init__(self):
        super().__init__(KaizenAwardPeriod)

    def get_by_code(self, award_code: str):
        return self.get_first_by(
            award_code=award_code
        )

    def exists_by_code(self, award_code: str) -> bool:
        return self.get_by_code(award_code) is not None

    def get_by_code_any_status(self, award_code: str):
        return (
            self.model.query
            .filter_by(award_code=award_code)
            .first()
        )