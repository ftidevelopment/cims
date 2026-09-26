from sqlalchemy import func

from app.extensions import db
from app.models.kaizen_award_score import KaizenAwardScore
from app.repositories.base_repository import BaseRepository
from app.models.kaizen import Kaizen

class KaizenAwardScoreRepository(BaseRepository):

    model = KaizenAwardScore

    searchable_fields = []

    sortable_fields = {
        "score": KaizenAwardScore.score,
        "scored_at": KaizenAwardScore.scored_at,
        "created_at": KaizenAwardScore.created_at,
    }

    def __init__(self):
        super().__init__(KaizenAwardScore)

    def get_by_award_period(self, award_period_id):

        return (
            self.model.query
            .filter_by(
                award_period_id=award_period_id,
                is_active=True
            )
            .order_by(
                self.model.kaizen_id.asc()
            )
            .all()
        )

    def get_by_kaizen(self, kaizen_id):

        return (
            self.model.query
            .filter_by(
                kaizen_id=kaizen_id,
                is_active=True
            )
            .all()
        )

    def get_by_judge(
        self,
        award_period_id,
        judge_employee_id
    ):

        return (
            self.model.query
            .filter_by(
                award_period_id=award_period_id,
                judge_employee_id=judge_employee_id,
                is_active=True
            )
            .order_by(
                self.model.kaizen_id.asc()
            )
            .all()
        )

    def get_by_kaizen_and_judge(
        self,
        award_period_id,
        kaizen_id,
        judge_employee_id
    ):

        return (
            self.model.query
            .filter_by(
                award_period_id=award_period_id,
                kaizen_id=kaizen_id,
                judge_employee_id=judge_employee_id
            )
            .first()
        )

    def get_scores_for_kaizen(
            self,
            award_period_id,
            kaizen_id
        ):

            return (
                self.model.query
                .filter_by(
                    award_period_id=award_period_id,
                    kaizen_id=kaizen_id,
                    is_active=True
                )
                .order_by(
                    self.model.judge_employee_id.asc()
                )
                .all()
            )

    def get_summary_by_award_period(
            self,
            award_period_id,
            start_date,
            end_date,
            page=1,
            per_page=10
        ):

        from datetime import datetime, time, timedelta
        from sqlalchemy import func

        # ==================================================
        # Award Period Date
        # ==================================================

        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        # ==================================================
        # Score Summary Subquery
        # ==================================================

        score_summary = (
            db.session.query(
                KaizenAwardScore.kaizen_id.label(
                    "kaizen_id"
                ),

                func.count(
                    KaizenAwardScore.id
                ).label(
                    "judges_scored"
                ),

                func.coalesce(
                    func.sum(
                        KaizenAwardScore.score
                    ),
                    0
                ).label(
                    "total_score"
                ),

                func.coalesce(
                    func.avg(
                        KaizenAwardScore.score
                    ),
                    0
                ).label(
                    "average_score"
                )
            )

            .filter(
                KaizenAwardScore.award_period_id
                == award_period_id,

                KaizenAwardScore.is_active.is_(True),

                KaizenAwardScore.scored_at.isnot(None)
            )

            .group_by(
                KaizenAwardScore.kaizen_id
            )

            .subquery()
        )

        # ==================================================
        # Main Kaizen Query
        # ==================================================

        query = (
            db.session.query(
                Kaizen,

                func.coalesce(
                    score_summary.c.judges_scored,
                    0
                ).label(
                    "judges_scored"
                ),

                func.coalesce(
                    score_summary.c.total_score,
                    0
                ).label(
                    "total_score"
                ),

                func.coalesce(
                    score_summary.c.average_score,
                    0
                ).label(
                    "average_score"
                )
            )

            .outerjoin(
                score_summary,
                score_summary.c.kaizen_id
                == Kaizen.id
            )

            # ==================================================
            # Kaizen Filter
            # ==================================================

            .filter(
                Kaizen.is_active.is_(True),

                Kaizen.status == "Approved",

                Kaizen.approved_at.isnot(None),

                Kaizen.approved_at >= start_datetime,

                Kaizen.approved_at < end_datetime
            )

            # ==================================================
            # Sorting
            # Highest Total Score First
            # ==================================================

            .order_by(
                func.coalesce(
                    score_summary.c.total_score,
                    0
                ).desc(),

                Kaizen.kaizen_no.asc()
            )
        )

        # ==================================================
        # Pagination
        # ==================================================

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )