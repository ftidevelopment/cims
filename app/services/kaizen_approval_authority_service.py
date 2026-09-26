from app.repositories.kaizen_approval_authority_repository import (
    KaizenApprovalAuthorityRepository,
)

from app.repositories.department_repository import (
    DepartmentRepository,
)

from app.repositories.employee_repository import (
    EmployeeRepository,
)

from app.services.base_service import (
    BaseService,
)

from app.core.transaction_manager import (
    TransactionManager,
)

from app.models.kaizen_approval_authority import (
    KaizenApprovalAuthority,
)


class KaizenApprovalAuthorityService(
    BaseService
):

    def __init__(self):

        super().__init__()

        # ==================================================
        # Repository
        # ==================================================

        self.repository = (
            KaizenApprovalAuthorityRepository()
        )

        self.department_repository = (
            DepartmentRepository()
        )

        self.employee_repository = (
            EmployeeRepository()
        )

    # ==========================================================
    # GET ACTIVE
    # ==========================================================

    def get_active(self):

        return (
            self.repository
            .get_active()
        )

    # ==========================================================
    # GET ALL
    # ==========================================================

    def get_all_authorities(self):

        return (
            self.repository
            .get_all_authorities()
        )

    # ==========================================================
    # FIND BY DEPARTMENT
    # ==========================================================

    def find_by_department(
        self,
        department_id,
    ):

        return (
            self.repository
            .find_by_department(
                department_id=department_id,
                active_only=True,
            )
        )

    # ==========================================================
    # FIND BY EMPLOYEE
    # ==========================================================

    def find_by_employee(
        self,
        employee_id,
    ):

        return (
            self.repository
            .find_by_employee(
                employee_id=employee_id,
                active_only=True,
            )
        )

    # ==========================================================
    # CHECK AUTHORITY
    # ==========================================================

    def has_authority(
        self,
        department_id,
        employee_id,
    ):
        """
        Check whether an employee has active
        Kaizen Approval Authority for a department.
        """

        return (
            self.repository
            .has_authority(
                department_id=department_id,
                employee_id=employee_id,
            )
        )

    # ==========================================================
    # ASSIGN AUTHORITY
    # ==========================================================

    def assign(
        self,
        department_id,
        employee_id,
        assigned_by=None,
    ):
        """
        Assign an employee as Kaizen Approval Authority
        for a specific department.

        One employee may have authority for
        multiple departments.
        """

        try:

            # ==============================================
            # Validate Department
            # ==============================================

            department = (
                self.department_repository
                .get_by_id(
                    department_id
                )
            )

            self.validate_exists(
                department,
                "Department",
            )

            # ==============================================
            # Validate Employee
            # ==============================================

            employee = (
                self.employee_repository
                .get_by_id(
                    employee_id
                )
            )

            self.validate_exists(
                employee,
                "Employee",
            )

            # ==============================================
            # Check Existing Authority
            # ==============================================

            authority = (
                self.repository
                .find_by_department_and_employee(
                    department_id=department_id,
                    employee_id=employee_id,
                    active_only=False,
                )
            )

            # ==============================================
            # Already Active
            # ==============================================

            if authority and authority.is_active:

                return self.failed(
                    "This employee is already assigned "
                    "as Kaizen Approval Authority "
                    "for this department."
                )

            # ==============================================
            # Reactivate Existing Inactive Record
            # ==============================================

            if authority and not authority.is_active:

                with TransactionManager():

                    authority.is_active = True

                    if assigned_by is not None:

                        authority.updated_by = (
                            assigned_by
                        )

                    self.repository.update(
                        authority
                    )

                return self.success(
                    "Kaizen Approval Authority "
                    "reactivated successfully.",
                    authority,
                )

            # ==============================================
            # Create New Authority
            # ==============================================

            with TransactionManager():

                authority = (
                    KaizenApprovalAuthority()
                )

                authority.department_id = (
                    department_id
                )

                authority.employee_id = (
                    employee_id
                )

                if assigned_by is not None:

                    authority.created_by = (
                        assigned_by
                    )

                    authority.updated_by = (
                        assigned_by
                    )

                self.repository.create(
                    authority
                )

            return self.success(
                "Kaizen Approval Authority "
                "assigned successfully.",
                authority,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================================
    # REMOVE AUTHORITY
    # ==========================================================

    def remove(
        self,
        department_id,
        employee_id,
        removed_by=None,
    ):
        """
        Remove Kaizen Approval Authority.

        Uses soft delete so the authority record
        remains available for audit/history.
        """

        try:

            # ==============================================
            # Get Authority
            # ==============================================

            authority = (
                self.repository
                .find_by_department_and_employee(
                    department_id=department_id,
                    employee_id=employee_id,
                    active_only=True,
                )
            )

            if not authority:

                return self.failed(
                    "Kaizen Approval Authority "
                    "was not found."
                )

            # ==============================================
            # Deactivate
            # ==============================================

            with TransactionManager():

                self.repository.deactivate(
                    authority=authority,
                    updated_by=removed_by,
                )

            return self.success(
                "Kaizen Approval Authority "
                "removed successfully.",
                authority,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================================
    # REACTIVATE AUTHORITY
    # ==========================================================

    def reactivate(
        self,
        department_id,
        employee_id,
        updated_by=None,
    ):
        """
        Reactivate an existing inactive authority.
        """

        try:

            # ==============================================
            # Find Inactive Authority
            # ==============================================

            authority = (
                self.repository
                .find_by_department_and_employee(
                    department_id=department_id,
                    employee_id=employee_id,
                    active_only=False,
                )
            )

            if not authority:

                return self.failed(
                    "Kaizen Approval Authority "
                    "was not found."
                )

            # ==============================================
            # Already Active
            # ==============================================

            if authority.is_active:

                return self.failed(
                    "Kaizen Approval Authority "
                    "is already active."
                )

            # ==============================================
            # Reactivate
            # ==============================================

            with TransactionManager():

                self.repository.reactivate(
                    authority=authority,
                    updated_by=updated_by,
                )

            return self.success(
                "Kaizen Approval Authority "
                "reactivated successfully.",
                authority,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )