from app.core.service_result import ServiceResult
from app.core.transaction_manager import TransactionManager

from app.repositories.kaizen_reporting_period_repository import (
    KaizenReportingPeriodRepository
)

from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService


class KaizenReportingPeriodService(BaseService, BaseExportService):
    """
    Service untuk mengelola Kaizen Reporting Period.
    """

    EXPORT_CONFIG = [
        {
            "header": "Period Code",
            "field": "period_code",
            "width": 20
        },
        {
            "header": "Period Name",
            "field": "period_name",
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
        self.repository = KaizenReportingPeriodRepository()
        self.transaction = TransactionManager()

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

    def get_by_id(self, reporting_period_id):
        return self.repository.get_by_id(reporting_period_id)

    # =========================================================
    # VALIDATE DATE RANGE
    # =========================================================

    def _validate_date_range(self, start_date, end_date):

        if not start_date:
            return self.failed("Start date is required.")

        if not end_date:
            return self.failed("End date is required.")

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
        Check apakah periode baru/update overlap
        dengan periode aktif yang sudah ada.
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
        period_code,
        period_name,
        start_date,
        end_date,
        description=None
    ):

        period_code = (
            period_code.strip()
            if period_code
            else None
        )

        period_name = (
            period_name.strip()
            if period_name
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
                period_code,
                "Period code"
            ),
            self.validate_required(
                period_name,
                "Period name"
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

        existing_period = self.repository.get_by_code_any_status(
            period_code
        )

        if existing_period:
            if not existing_period.is_active:
                return self.failed(
                    "Reporting period code already exists but is inactive. "
                    "Please restore the existing period instead."
                )

            return self.failed(
                "Reporting period code already exists."
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
                "Reporting period overlaps with "
                "an existing active period."
            )

        # -----------------------------------------------------
        # Create object
        # -----------------------------------------------------

        from app.models.kaizen_reporting_period import (
            KaizenReportingPeriod
        )

        reporting_period = KaizenReportingPeriod(
            period_code=period_code,
            period_name=period_name,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

        try:

            with TransactionManager() as transaction:

                self.repository.create(
                    reporting_period
                )

                transaction.flush()
                transaction.refresh(
                    reporting_period
                )

            return self.success(
                "Kaizen reporting period created successfully.",
                reporting_period
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
        reporting_period,
        period_name,
        start_date,
        end_date,
        description=None
    ):

        if not reporting_period:
            return self.failed(
                "Reporting period not found."
            )

        period_name = (
            period_name.strip()
            if period_name
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
                period_name,
                "Period name"
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
            exclude_id=reporting_period.id
        ):
            return self.failed(
                "Reporting period overlaps with "
                "an existing active period."
            )

        # -----------------------------------------------------
        # Update
        # -----------------------------------------------------

        reporting_period.period_name = period_name
        reporting_period.start_date = start_date
        reporting_period.end_date = end_date
        reporting_period.description = description

        try:

            with TransactionManager() as transaction:

                self.repository.update(
                    reporting_period
                )

                transaction.flush()
                transaction.refresh(
                    reporting_period
                )

            return self.success(
                "Kaizen reporting period updated successfully.",
                reporting_period
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # =========================================================
    # DELETE
    # =========================================================

    def delete(self, reporting_period):

        if not reporting_period:
            return self.failed(
                "Reporting period not found."
            )

        try:

            with TransactionManager() as transaction:

                self.repository.delete(
                    reporting_period
                )

                transaction.flush()

            return self.success(
                "Kaizen reporting period deleted successfully.",
                reporting_period
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

    def restore(self, reporting_period_id):

        reporting_period = self.repository.restore(
            reporting_period_id
        )

        if not reporting_period:
            return ServiceResult(
                success=False,
                message="Kaizen reporting period not found."
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Kaizen reporting period restored successfully."
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
            sheet_name="Kaizen Reporting Period",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )