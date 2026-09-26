from datetime import datetime

from app.core.service_result import ServiceResult
from app.core.transaction_manager import TransactionManager

from app.models.kaizen_award_score import KaizenAwardScore

from app.repositories.kaizen_award_score_repository import (
    KaizenAwardScoreRepository
)
from app.services.kaizen_award_judge_service import (
    KaizenAwardJudgeService
)

from app.services.base_service import BaseService


class KaizenAwardScoreService(BaseService):

    def __init__(self):

        self.repository = KaizenAwardScoreRepository()
        self.transaction = TransactionManager()
        self.judge_service = KaizenAwardJudgeService()

    def get_by_award_period(self, award_period_id):

        return self.repository.get_by_award_period(
            award_period_id
        )

    def get_by_judge(
        self,
        award_period_id,
        judge_employee_id
    ):

        return self.repository.get_by_judge(
            award_period_id=award_period_id,
            judge_employee_id=judge_employee_id
        )

    def get_by_kaizen_and_judge(
        self,
        award_period_id,
        kaizen_id,
        judge_employee_id
    ):

        return self.repository.get_by_kaizen_and_judge(
            award_period_id=award_period_id,
            kaizen_id=kaizen_id,
            judge_employee_id=judge_employee_id
        )

    def create_or_update(
        self,
        award_period_id,
        kaizen_id,
        judge_employee_id,
        score,
        comment=None
    ):

        try:

            if not award_period_id:
                return ServiceResult(
                    success=False,
                    message="Award period is required."
                )

            if not kaizen_id:
                return ServiceResult(
                    success=False,
                    message="Kaizen is required."
                )

            if not judge_employee_id:
                return ServiceResult(
                    success=False,
                    message="Judge is required."
                )

            is_judge = self.judge_service.is_judge(
                award_period_id=award_period_id,
                employee_id=judge_employee_id
            )

            if not is_judge:

                return ServiceResult(
                    success=False,
                    message="Employee is not registered as Judge for this Award Period."
                )

            if score is None:
                return ServiceResult(
                    success=False,
                    message="Score is required."
                )

            try:
                score = float(score)
            except (TypeError, ValueError):

                return ServiceResult(
                    success=False,
                    message="Score must be a number."
                )

            if score < 0 or score > 100:

                return ServiceResult(
                    success=False,
                    message="Score must be between 0 and 100."
                )

            existing = self.repository.get_by_kaizen_and_judge(
                award_period_id=award_period_id,
                kaizen_id=kaizen_id,
                judge_employee_id=judge_employee_id
            )

            with TransactionManager() as transaction:

                if existing:

                    existing.score = score
                    existing.comment = comment
                    existing.scored_at = datetime.utcnow()

                    self.repository.update(existing)

                    transaction.flush()
                    transaction.refresh(existing)

                    return ServiceResult(
                        success=True,
                        message="Score updated successfully.",
                        data=existing
                    )

                score_data = KaizenAwardScore(
                    award_period_id=award_period_id,
                    kaizen_id=kaizen_id,
                    judge_employee_id=judge_employee_id,
                    score=score,
                    comment=comment,
                    scored_at=datetime.utcnow()
                )

                self.repository.create(score_data)

                transaction.flush()
                transaction.refresh(score_data)

            return ServiceResult(
                success=True,
                message="Score saved successfully.",
                data=score_data
            )

        except Exception as e:

            return self.handle_exception(
                e,
                "Failed to save score."
            )

    def get_summary_by_award_period(
            self,
            award_period_id,
            start_date,
            end_date,
            page=1,
            per_page=10
        ):

        return self.repository.get_summary_by_award_period(
            award_period_id=award_period_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )