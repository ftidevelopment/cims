from app.core.service_result import ServiceResult
from app.core.transaction_manager import TransactionManager

from app.models.kaizen_department_target import KaizenDepartmentTarget

from app.repositories.kaizen_department_target_repository import (
    KaizenDepartmentTargetRepository
)

from app.repositories.kaizen_reporting_period_repository import (
    KaizenReportingPeriodRepository
)

from app.repositories.department_repository import (
    DepartmentRepository
)

from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService


class KaizenDepartmentTargetService(BaseService, BaseExportService):

    EXPORT_CONFIG = [
        {
            "header": "Reporting Period",
            "field": "reporting_period_name",
            "width": 30
        },
        {
            "header": "Department",
            "field": "department_name",
            "width": 30
        },
        {
            "header": "Target",
            "field": "target_quantity",
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
        self.repository = KaizenDepartmentTargetRepository()
        self.reporting_period_repository = (
            KaizenReportingPeriodRepository()
        )
        self.department_repository = DepartmentRepository()
        self.transaction = TransactionManager()

    # ==========================================================
    # GET ALL
    # ==========================================================

    def get_all(
        self,
        keyword=None,
        is_active=True,
        department_id=None,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="asc"
    ):

        return self.repository.get_all(
            keyword=keyword,
            is_active=is_active,
            department_id=department_id,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    # ==========================================================
    # GET BY ID
    # ==========================================================

    def get_by_id(self, target_id):
        return self.repository.get_by_id(target_id)

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(
        self,
        reporting_period_id,
        department_id,
        target_quantity,
        description=None
    ):

        description = (
            description.strip()
            if description
            else None
        )

        validation = self.validate(
            self.validate_required(
                reporting_period_id,
                "Reporting period"
            ),
            self.validate_required(
                department_id,
                "Department"
            ),
            self.validate_required(
                target_quantity,
                "Target quantity"
            ),
        )

        if not validation.success:
            return validation

        # ------------------------------------------------------
        # Validate target quantity
        # ------------------------------------------------------

        try:
            target_quantity = int(target_quantity)
        except (TypeError, ValueError):
            return self.failed(
                "Target quantity must be a valid number."
            )

        if target_quantity <= 0:
            return self.failed(
                "Target quantity must be greater than 0."
            )

        # ------------------------------------------------------
        # Validate reporting period
        # ------------------------------------------------------

        reporting_period = (
            self.reporting_period_repository.get_by_id(
                reporting_period_id
            )
        )

        if not reporting_period:
            return self.failed(
                "Reporting period not found."
            )

        if not reporting_period.is_active:
            return self.failed(
                "Reporting period is inactive."
            )

        # ------------------------------------------------------
        # Validate department
        # ------------------------------------------------------

        department = (
            self.department_repository.get_by_id(
                department_id
            )
        )

        if not department:
            return self.failed(
                "Department not found."
            )

        if not department.is_active:
            return self.failed(
                "Department is inactive."
            )

        # ------------------------------------------------------
        # Validate duplicate
        # ------------------------------------------------------

        existing_target = (
            self.repository.get_by_period_and_department(
                reporting_period_id,
                department_id
            )
        )

        if existing_target:
            return self.failed(
                "Kaizen target for this department "
                "and reporting period already exists."
            )

        # ------------------------------------------------------
        # Create
        # ------------------------------------------------------

        target = KaizenDepartmentTarget(
            reporting_period_id=reporting_period_id,
            department_id=department_id,
            target_quantity=target_quantity,
            description=description,
        )

        try:

            with TransactionManager() as transaction:

                self.repository.create(target)

                transaction.flush()
                transaction.refresh(target)

            return self.success(
                "Kaizen department target created successfully.",
                target
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        target,
        reporting_period_id,
        department_id,
        target_quantity,
        description=None
    ):

        if not target:
            return self.failed(
                "Kaizen department target not found."
            )

        description = (
            description.strip()
            if description
            else None
        )

        validation = self.validate(
            self.validate_required(
                reporting_period_id,
                "Reporting period"
            ),
            self.validate_required(
                department_id,
                "Department"
            ),
            self.validate_required(
                target_quantity,
                "Target quantity"
            ),
        )

        if not validation.success:
            return validation

        # ------------------------------------------------------
        # Validate target quantity
        # ------------------------------------------------------

        try:
            target_quantity = int(target_quantity)
        except (TypeError, ValueError):
            return self.failed(
                "Target quantity must be a valid number."
            )

        if target_quantity <= 0:
            return self.failed(
                "Target quantity must be greater than 0."
            )

        # ------------------------------------------------------
        # Validate reporting period
        # ------------------------------------------------------

        reporting_period = (
            self.reporting_period_repository.get_by_id(
                reporting_period_id
            )
        )

        if not reporting_period:
            return self.failed(
                "Reporting period not found."
            )

        if not reporting_period.is_active:
            return self.failed(
                "Reporting period is inactive."
            )

        # ------------------------------------------------------
        # Validate department
        # ------------------------------------------------------

        department = (
            self.department_repository.get_by_id(
                department_id
            )
        )

        if not department:
            return self.failed(
                "Department not found."
            )

        if not department.is_active:
            return self.failed(
                "Department is inactive."
            )

        # ------------------------------------------------------
        # Validate duplicate
        # ------------------------------------------------------

        existing_target = (
            self.repository.get_by_period_and_department(
                reporting_period_id,
                department_id
            )
        )

        if (
            existing_target
            and existing_target.id != target.id
        ):
            return self.failed(
                "Kaizen target for this department "
                "and reporting period already exists."
            )

        # ------------------------------------------------------
        # Update
        # ------------------------------------------------------

        target.reporting_period_id = reporting_period_id
        target.department_id = department_id
        target.target_quantity = target_quantity
        target.description = description

        try:

            with TransactionManager() as transaction:

                self.repository.update(target)

                transaction.flush()
                transaction.refresh(target)

            return self.success(
                "Kaizen department target updated successfully.",
                target
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(self, target):

        if not target:
            return self.failed(
                "Kaizen department target not found."
            )

        try:

            with TransactionManager() as transaction:

                self.repository.delete(target)

                transaction.flush()

            return self.success(
                "Kaizen department target deleted successfully.",
                target
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==========================================================
    # INACTIVE
    # ==========================================================

    def get_inactive(self):
        return self.repository.get_inactive()

    # ==========================================================
    # RESTORE
    # ==========================================================

    def restore(self, target_id):

        target = self.repository.restore(
            target_id
        )

        if not target:
            return ServiceResult(
                success=False,
                message="Kaizen department target not found."
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Kaizen department target restored successfully."
        )

    # ==========================================================
    # EXPORT
    # ==========================================================

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc"
    ):

        return self.export(
            sheet_name="Kaizen Department Target",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )