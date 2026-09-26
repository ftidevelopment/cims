from flask import current_app, render_template
from app.core.service_result import ServiceResult
from app.core.transaction_manager import TransactionManager

from app.repositories.kaizen_award_period_repository import (
    KaizenAwardPeriodRepository
)

from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService
from app.core.notification_events import NotificationEvent
from app.services.notification_service import NotificationService
from app.repositories.kaizen_award_score_repository import (
    KaizenAwardScoreRepository
)

class KaizenAwardPeriodService(BaseService, BaseExportService):
    """
    Service untuk mengelola Kaizen Award Period.
    """

    EXPORT_CONFIG = [
        {
            "header": "Award Code",
            "field": "award_code",
            "width": 20
        },
        {
            "header": "Award Name",
            "field": "award_name",
            "width": 35
        },
        {
            "header": "Start Date",
            "field": "start_date",
            "width": 15
        },
        {
            "header": "End Date",
            "field": "end_date",
            "width": 15
        },
        {
            "header": "Description",
            "field": "description",
            "width": 50
        },
        {
            "header": "Status",
            "field": "is_active",
            "width": 15
        },
    ]

    def __init__(self):
        self.repository = KaizenAwardPeriodRepository()
        self.transaction = TransactionManager()
        self.kaizen_award_score_repository = (
        KaizenAwardScoreRepository()
        )
        self.notification_service = NotificationService()

    # =========================================================
    # GET ALL
    # =========================================================

    def get_all(
        self,
        keyword=None,
        is_active=True,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="asc"
    ):
        return self.repository.get_all(
            keyword=keyword,
            is_active=is_active,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    # =========================================================
    # GET BY ID
    # =========================================================

    def get_by_id(self, award_period_id):
        return self.repository.get_by_id(
            award_period_id
        )

    # =========================================================
    # VALIDATE DATE RANGE
    # =========================================================

    def _validate_date_range(
        self,
        start_date,
        end_date
    ):

        if not start_date:
            return self.failed(
                "Start date is required."
            )

        if not end_date:
            return self.failed(
                "End date is required."
            )

        if start_date > end_date:
            return self.failed(
                "Start date cannot be later than end date."
            )

        return self.success()

    # =========================================================
    # CHECK PERIOD OVERLAP
    # =========================================================

    def _has_overlap(
        self,
        start_date,
        end_date,
        exclude_id=None
    ):
        """
        Check apakah Award Period baru/update overlap
        dengan Award Period aktif yang sudah ada.
        """

        periods = self.repository.get_export_data(
            is_active=True,
            sort_by="start_date",
            sort_order="asc",
        )

        for period in periods:

            if exclude_id and period.id == exclude_id:
                continue

            if (
                period.start_date <= end_date
                and period.end_date >= start_date
            ):
                return True

        return False

    # =========================================================
    # CREATE
    # =========================================================

    def create(
        self,
        award_code,
        award_name,
        start_date,
        end_date,
        description=None
    ):

        award_code = (
            award_code.strip()
            if award_code
            else None
        )

        award_name = (
            award_name.strip()
            if award_name
            else None
        )

        description = (
            description.strip()
            if description
            else None
        )

        # -----------------------------------------------------
        # Required validation
        # -----------------------------------------------------

        validation = self.validate(
            self.validate_required(
                award_code,
                "Award code"
            ),
            self.validate_required(
                award_name,
                "Award name"
            ),
            self.validate_required(
                start_date,
                "Start date"
            ),
            self.validate_required(
                end_date,
                "End date"
            ),
        )

        if not validation.success:
            return validation

        # -----------------------------------------------------
        # Duplicate code
        # -----------------------------------------------------

        existing_period = (
            self.repository.get_by_code_any_status(
                award_code
            )
        )

        if existing_period:

            if not existing_period.is_active:
                return self.failed(
                    "Award period code already exists but is inactive. "
                    "Please restore the existing period instead."
                )

            return self.failed(
                "Award period code already exists."
            )

        # -----------------------------------------------------
        # Date validation
        # -----------------------------------------------------

        validation = self._validate_date_range(
            start_date,
            end_date
        )

        if not validation.success:
            return validation

        # -----------------------------------------------------
        # Overlap validation
        # -----------------------------------------------------

        if self._has_overlap(
            start_date,
            end_date
        ):
            return self.failed(
                "Award period overlaps with "
                "an existing active period."
            )

        # -----------------------------------------------------
        # Create object
        # -----------------------------------------------------

        from app.models.kaizen_award_period import (
            KaizenAwardPeriod
        )

        award_period = KaizenAwardPeriod(
            award_code=award_code,
            award_name=award_name,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

        try:

            with TransactionManager() as transaction:

                self.repository.create(
                    award_period
                )

                transaction.flush()
                transaction.refresh(
                    award_period
                )

            return self.success(
                "Kaizen award period created successfully.",
                award_period
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        award_period,
        award_name,
        start_date,
        end_date,
        description=None
    ):

        if not award_period:
            return self.failed(
                "Award period not found."
            )

        award_name = (
            award_name.strip()
            if award_name
            else None
        )

        description = (
            description.strip()
            if description
            else None
        )

        # -----------------------------------------------------
        # Required validation
        # -----------------------------------------------------

        validation = self.validate(
            self.validate_required(
                award_name,
                "Award name"
            ),
            self.validate_required(
                start_date,
                "Start date"
            ),
            self.validate_required(
                end_date,
                "End date"
            ),
        )

        if not validation.success:
            return validation

        # -----------------------------------------------------
        # Date validation
        # -----------------------------------------------------

        validation = self._validate_date_range(
            start_date,
            end_date
        )

        if not validation.success:
            return validation

        # -----------------------------------------------------
        # Overlap validation
        # -----------------------------------------------------

        if self._has_overlap(
            start_date,
            end_date,
            exclude_id=award_period.id
        ):
            return self.failed(
                "Award period overlaps with "
                "an existing active period."
            )

        # -----------------------------------------------------
        # Update
        # -----------------------------------------------------

        award_period.award_name = award_name
        award_period.start_date = start_date
        award_period.end_date = end_date
        award_period.description = description

        try:

            with TransactionManager() as transaction:

                self.repository.update(
                    award_period
                )

                transaction.flush()
                transaction.refresh(
                    award_period
                )

            return self.success(
                "Kaizen award period updated successfully.",
                award_period
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # =========================================================
    # DELETE
    # =========================================================

    def delete(self, award_period):

        if not award_period:
            return self.failed(
                "Award period not found."
            )

        try:

            with TransactionManager() as transaction:

                self.repository.delete(
                    award_period
                )

                transaction.flush()

            return self.success(
                "Kaizen award period deleted successfully.",
                award_period
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # =========================================================
    # GET INACTIVE
    # =========================================================

    def get_inactive(self):

        return self.repository.get_inactive()

    # =========================================================
    # RESTORE
    # =========================================================

    def restore(self, award_period_id):

        award_period = self.repository.restore(
            award_period_id
        )

        if not award_period:
            return ServiceResult(
                success=False,
                message="Kaizen award period not found."
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Kaizen award period restored successfully."
        )

    # =========================================================
    # EXPORT EXCEL
    # =========================================================

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc"
    ):

        return self.export(
            sheet_name="Kaizen Award Period",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )


    # =========================================================
    # CLOSE AWARD PERIOD
    # =========================================================

    def close(self, award_period_id):

        try:

            # -------------------------------------------------
            # Get Award Period
            # -------------------------------------------------

            award_period = self.repository.get_by_id(
                award_period_id
            )

            if not award_period:

                return ServiceResult(
                    success=False,
                    message="Kaizen award period not found."
                )

            # -------------------------------------------------
            # Check Status
            # -------------------------------------------------

            if award_period.status == "Closed":

                return ServiceResult(
                    success=False,
                    message="Kaizen award period is already closed."
                )

            # -------------------------------------------------
            # Close Period
            # -------------------------------------------------

            with TransactionManager() as transaction:

                award_period.status = "Closed"

                self.repository.update(
                    award_period
                )

                transaction.flush()

                transaction.refresh(
                    award_period
                )

            # =================================================
            # DATABASE COMMIT SUCCESS
            # =================================================
            #
            # Award Period sudah berhasil Closed.
            #
            # Notification tidak dikirim langsung.
            # Notification dimasukkan ke Celery Queue.
            #
            # Celery hanya menerima award_period.id.
            # Worker akan mengambil ulang Award Period
            # dan menghitung Top 5 dari database.
            # =================================================

            try:

                from app.tasks.notification_tasks import (
                    send_kaizen_award_notification
                )

                task = (
                    send_kaizen_award_notification
                    .delay(
                        award_period.id
                    )
                )

                print(
                    "=========================================="
                )

                print(
                    "KAIZEN AWARD NOTIFICATION "
                    "SUCCESSFULLY QUEUED"
                )

                print(
                    "Award Period ID:",
                    award_period.id
                )

                print(
                    "Award Code:",
                    award_period.award_code
                )

                print(
                    "Award Name:",
                    award_period.award_name
                )

                print(
                    "Task ID:",
                    task.id
                )

                print(
                    "=========================================="
                )

            except Exception as ex:

                print(
                    "KAIZEN AWARD CELERY "
                    "NOTIFICATION QUEUE ERROR:",
                    str(ex)
                )

            # -------------------------------------------------
            # Success
            # -------------------------------------------------

            return ServiceResult(
                success=True,
                message="Kaizen award period closed successfully.",
                data=award_period
            )

        except Exception as exception:

            return self.handle_exception(
                exception,
                "Failed to close Kaizen award period."
            )