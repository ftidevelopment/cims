from app.models.improvement_approval_authority import (
    ImprovementApprovalAuthority,
)

from app.repositories.improvement_approval_authority_repository import (
    ImprovementApprovalAuthorityRepository,
)

from app.repositories.employee_repository import (
    EmployeeRepository,
)

from app.repositories.department_repository import (
    DepartmentRepository,
)

from app.services.base_service import (
    BaseService,
)

from app.core.transaction_manager import (
    TransactionManager,
)


class ImprovementApprovalAuthorityService(
    BaseService
):

    def __init__(self):

        super().__init__()

        self.authority_repository = (
            ImprovementApprovalAuthorityRepository()
        )

        self.employee_repository = (
            EmployeeRepository()
        )

        self.department_repository = (
            DepartmentRepository()
        )

    # ==================================================
    # ASSIGN AUTHORITY
    # ==================================================

    def assign(
        self,
        department_id,
        employee_id,
        assigned_by=None,
    ):
        """
        Assign an employee as an Improvement
        Approval Authority for a department.

        Validation:
        - Department must exist
        - Department must be active
        - Employee must exist
        - Employee must be active
        - Employee must have a User Account
        - Duplicate authority is not allowed
        - Existing inactive authority will be reactivated
        """

        try:

            # ==========================================
            # Validate Department
            # ==========================================

            department = (
                self.department_repository
                .get_by_id(
                    department_id
                )
            )

            if not department:

                return self.failed(
                    "Department not found."
                )

            if hasattr(
                department,
                "is_active"
            ) and not department.is_active:

                return self.failed(
                    "Department is inactive."
                )

            # ==========================================
            # Validate Employee
            # ==========================================

            employee = (
                self.employee_repository
                .get_by_id(
                    employee_id
                )
            )

            if not employee:

                return self.failed(
                    "Employee not found."
                )

            # ==========================================
            # Validate Employee Status
            # ==========================================

            if not employee.is_active:

                return self.failed(
                    "Employee is inactive."
                )

            # ==========================================
            # Validate User Account
            # ==========================================

            if not employee.user:

                return self.failed(
                    "Selected employee does not "
                    "have a User Account."
                )

            # ==========================================
            # Check Existing Authority
            # ==========================================

            authority = (
                self.authority_repository
                .find_by_department_and_employee(
                    department_id=department_id,
                    employee_id=employee_id,
                    active_only=False,
                )
            )

            # ==========================================
            # Already Active
            # ==========================================

            if authority:

                if authority.is_active:

                    return self.failed(
                        "This employee already has "
                        "Improvement Approval Authority "
                        "for this department."
                    )

                # ======================================
                # Reactivate Existing Authority
                # ======================================

                with TransactionManager():

                    authority.is_active = True

                    authority.updated_by = (
                        assigned_by
                    )

                    self.authority_repository.update(
                        authority
                    )

                return self.success(
                    "Improvement Approval Authority "
                    "reactivated successfully.",
                    authority,
                )

            # ==========================================
            # Create New Authority
            # ==========================================

            authority = (
                ImprovementApprovalAuthority()
            )

            authority.department_id = (
                department_id
            )

            authority.employee_id = (
                employee_id
            )

            authority.is_active = True

            authority.created_by = (
                assigned_by
            )

            authority.updated_by = (
                assigned_by
            )

            with TransactionManager():

                self.authority_repository.create(
                    authority
                )

            return self.success(
                "Improvement Approval Authority "
                "assigned successfully.",
                authority,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==================================================
    # REMOVE / REVOKE AUTHORITY
    # ==================================================

    def remove(
        self,
        department_id,
        employee_id,
        removed_by=None,
    ):
        """
        Revoke Improvement Approval Authority.

        Uses soft delete by setting is_active=False.
        """

        try:

            # ==========================================
            # Find Authority
            # ==========================================

            authority = (
                self.authority_repository
                .find_by_department_and_employee(
                    department_id=department_id,
                    employee_id=employee_id,
                    active_only=True,
                )
            )

            if not authority:

                return self.failed(
                    "Active Improvement Approval "
                    "Authority not found."
                )

            # ==========================================
            # Deactivate Authority
            # ==========================================

            with TransactionManager():

                authority.is_active = False

                authority.updated_by = (
                    removed_by
                )

                self.authority_repository.update(
                    authority
                )

            return self.success(
                "Improvement Approval Authority "
                "removed successfully.",
                authority,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==================================================
    # REACTIVATE AUTHORITY
    # ==================================================

    def reactivate(
        self,
        department_id,
        employee_id,
        updated_by=None,
    ):
        """
        Reactivate an existing inactive
        Improvement Approval Authority.
        """

        try:

            authority = (
                self.authority_repository
                .find_by_department_and_employee(
                    department_id=department_id,
                    employee_id=employee_id,
                    active_only=False,
                )
            )

            if not authority:

                return self.failed(
                    "Improvement Approval "
                    "Authority not found."
                )

            if authority.is_active:

                return self.failed(
                    "This authority is already active."
                )

            # ==========================================
            # Validate Employee Again
            # ==========================================

            employee = (
                self.employee_repository
                .get_by_id(
                    employee_id
                )
            )

            if not employee:

                return self.failed(
                    "Employee not found."
                )

            if not employee.is_active:

                return self.failed(
                    "Employee is inactive."
                )

            if not employee.user:

                return self.failed(
                    "Selected employee does not "
                    "have a User Account."
                )

            # ==========================================
            # Reactivate
            # ==========================================

            with TransactionManager():

                authority.is_active = True

                authority.updated_by = (
                    updated_by
                )

                self.authority_repository.update(
                    authority
                )

            return self.success(
                "Improvement Approval Authority "
                "reactivated successfully.",
                authority,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==================================================
    # GET BY DEPARTMENT
    # ==================================================

    def get_by_department(
        self,
        department_id,
    ):
        """
        Get active approval authorities
        for a department.
        """

        return (
            self.authority_repository
            .find_by_department(
                department_id=department_id,
                active_only=True,
            )
        )

    # ==================================================
    # GET BY EMPLOYEE
    # ==================================================

    def get_by_employee(
        self,
        employee_id,
    ):
        """
        Get active departments where the employee
        has approval authority.
        """

        return (
            self.authority_repository
            .find_by_employee(
                employee_id=employee_id,
                active_only=True,
            )
        )

    # ==================================================
    # CHECK AUTHORITY
    # ==================================================

    def has_authority(
        self,
        department_id,
        employee_id,
    ):
        """
        Check whether an employee has active
        Improvement Approval Authority for
        the specified department.
        """

        return (
            self.authority_repository
            .has_authority(
                department_id=department_id,
                employee_id=employee_id,
            )
        )

    # ==================================================
    # GET ACTIVE
    # ==================================================

    def get_active(self):

        return (
            self.authority_repository
            .get_active()
        )

    # ==================================================
    # GET ALL
    # ==================================================

    def get_all(self):

        return (
            self.authority_repository
            .get_all_authorities()
        )