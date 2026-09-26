from app.models.kaizen_reporting_period import KaizenReportingPeriod
from app.repositories.base_repository import BaseRepository


class KaizenReportingPeriodRepository(BaseRepository):

    model = KaizenReportingPeriod

    searchable_fields = [
        KaizenReportingPeriod.period_code,
        KaizenReportingPeriod.period_name,
        KaizenReportingPeriod.description,
    ]

    sortable_fields = {
        "period_code": KaizenReportingPeriod.period_code,
        "period_name": KaizenReportingPeriod.period_name,
        "start_date": KaizenReportingPeriod.start_date,
        "end_date": KaizenReportingPeriod.end_date,
        "created_at": KaizenReportingPeriod.created_at,
    }

    def __init__(self):
        super().__init__(KaizenReportingPeriod)

    def get_by_code(self, period_code: str):
        return self.get_first_by(
            period_code=period_code
        )

    def exists_by_code(self, period_code: str) -> bool:
        return self.get_by_code(period_code) is not None

    def get_by_code_any_status(self, period_code: str):
        return (
            self.model.query
            .filter_by(period_code=period_code)
            .first()
        )