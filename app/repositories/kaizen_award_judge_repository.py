from app.models.kaizen_award_judge import KaizenAwardJudge
from app.repositories.base_repository import BaseRepository


class KaizenAwardJudgeRepository(BaseRepository):

    model = KaizenAwardJudge

    searchable_fields = []

    sortable_fields = {
        "created_at": KaizenAwardJudge.created_at,
    }

    def __init__(self):
        super().__init__(KaizenAwardJudge)

    def get_by_award_period(self, award_period_id):
        return (
            self.model.query
            .filter_by(
                award_period_id=award_period_id,
                is_active=True
            )
            .order_by(self.model.id.asc())
            .all()
        )

    def get_by_employee(
        self,
        award_period_id,
        employee_id
    ):
        return (
            self.model.query
            .filter_by(
                award_period_id=award_period_id,
                employee_id=employee_id
            )
            .first()
        )

    def get_by_award_period_and_employee(
        self,
        award_period_id,
        employee_id
    ):
        return (
            self.model.query
            .filter_by(
                award_period_id=award_period_id,
                employee_id=employee_id,
                is_active=True
            )
            .first()
        )