from app.core.service_result import ServiceResult
from app.core.transaction_manager import TransactionManager

from app.models.kaizen_award_judge import KaizenAwardJudge

from app.repositories.kaizen_award_judge_repository import (
    KaizenAwardJudgeRepository
)

from app.services.base_service import BaseService


class KaizenAwardJudgeService(BaseService):

    def __init__(self):
        self.repository = KaizenAwardJudgeRepository()
        self.transaction = TransactionManager()

    # =========================================================
    # GET JUDGES BY AWARD PERIOD
    # =========================================================
    def get_by_award_period(self, award_period_id):

        return self.repository.get_by_award_period(
            award_period_id
        )

    # =========================================================
    # GET JUDGE BY ID
    # =========================================================
    def get_by_id(self, judge_id):

        return self.repository.get_by_id(
            judge_id
        )

    # =========================================================
    # CREATE / ADD JUDGE
    # =========================================================
    def create(
        self,
        award_period_id,
        employee_id
    ):

        try:

            # -------------------------------------------------
            # Validate Award Period
            # -------------------------------------------------
            if not award_period_id:

                return ServiceResult(
                    success=False,
                    message="Award period is required."
                )

            # -------------------------------------------------
            # Validate Employee
            # -------------------------------------------------
            if not employee_id:

                return ServiceResult(
                    success=False,
                    message="Employee is required."
                )

            # -------------------------------------------------
            # Check existing assignment
            # -------------------------------------------------
            existing = self.repository.get_by_employee(
                award_period_id=award_period_id,
                employee_id=employee_id
            )

            # -------------------------------------------------
            # Existing Judge
            # -------------------------------------------------
            if existing:

                # Existing but inactive
                if not existing.is_active:

                    existing.is_active = True

                    with TransactionManager() as transaction:

                        transaction.flush()
                        transaction.refresh(existing)

                    return ServiceResult(
                        success=True,
                        message="Judge restored successfully.",
                        data=existing
                    )

                # Existing and active
                return ServiceResult(
                    success=False,
                    message="Employee is already assigned as Judge."
                )

            # -------------------------------------------------
            # Create new Judge
            # -------------------------------------------------
            judge = KaizenAwardJudge(
                award_period_id=award_period_id,
                employee_id=employee_id
            )

            with TransactionManager() as transaction:

                self.repository.create(judge)

                transaction.flush()
                transaction.refresh(judge)

            return ServiceResult(
                success=True,
                message="Judge added successfully.",
                data=judge
            )

        except Exception as e:

            return self.handle_exception(
                e,
                "Failed to add Judge."
            )

    # =========================================================
    # DELETE / SOFT DELETE JUDGE
    # =========================================================
    def delete(self, judge):

        try:

            if not judge:

                return ServiceResult(
                    success=False,
                    message="Judge not found."
                )

            with TransactionManager() as transaction:

                self.repository.delete(judge)

                transaction.flush()

            return ServiceResult(
                success=True,
                message="Judge removed successfully."
            )

        except Exception as e:

            return self.handle_exception(
                e,
                "Failed to remove Judge."
            )

    # =========================================================
    # GET INACTIVE JUDGES
    # =========================================================
    def get_inactive(self):

        return self.repository.get_inactive()

    # =========================================================
    # RESTORE JUDGE
    # =========================================================
    def restore(self, judge_id):

        try:

            judge = self.repository.restore(
                judge_id
            )

            if not judge:

                return ServiceResult(
                    success=False,
                    message="Inactive Judge not found."
                )

            with TransactionManager() as transaction:

                transaction.flush()
                transaction.refresh(judge)

            return ServiceResult(
                success=True,
                message="Judge restored successfully.",
                data=judge
            )
        

        except Exception as e:

            return self.handle_exception(
                e,
                "Failed to restore Judge."
            )

    def is_judge(
        self,
        award_period_id,
        employee_id
    ):
        judge = self.repository.get_by_award_period_and_employee(
            award_period_id=award_period_id,
            employee_id=employee_id
        )

        return judge is not None