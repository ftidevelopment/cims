from app.models.problem_assignment_authority import (
    ProblemAssignmentAuthority,
)

from app.repositories.problem_assignment_authority_repository import (
    ProblemAssignmentAuthorityRepository,
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


class ProblemAssignmentAuthorityService(
    BaseService
):

    """
    Service untuk mengelola user/employee yang memiliki
    kewenangan melakukan Assign Problem berdasarkan
    department.

    Rule:
    - Employee harus ACTIVE
    - Employee harus mempunyai User Account
    - Department harus ada
    - Satu employee dapat menjadi authority
      di beberapa department
    - Satu department dapat mempunyai beberapa authority
    """

    def __init__(self):

        super().__init__()

        self.repository = (
            ProblemAssignmentAuthorityRepository()
        )

        self.employee_repository = (
            EmployeeRepository()
        )

        self.department_repository = (
            DepartmentRepository()
        )

    # ==================================================
    # GET BY DEPARTMENT
    # ==================================================

    def get_by_department(
        self,
        department_id,
        is_active=True,
    ):
        """
        Get all assignment authorities
        for a department.
        """

        return (
            self.repository
            .find_by_department(
                department_id=department_id,
                is_active=is_active,
            )
        )

    # ==================================================
    # GET BY EMPLOYEE
    # ==================================================

    def get_by_employee(
        self,
        employee_id,
        is_active=True,
    ):
        """
        Get all departments where an employee
        has assignment authority.
        """

        return (
            self.repository
            .find_by_employee(
                employee_id=employee_id,
                is_active=is_active,
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
        assignment authority for a department.
        """

        return (
            self.repository
            .has_authority(
                department_id=department_id,
                employee_id=employee_id,
            )
        )

    # ==================================================
    # ASSIGN AUTHORITY
    # ==================================================

    def assign(
        self,
        department_id,
        employee_id,
        created_by=None,
    ):
        """
        Assign an employee as Problem Assignment
        Authority for a specific department.
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
                    f"Employee "
                    f"{employee.full_name} "
                    f"is inactive."
                )

            # ==========================================
            # Validate User Account
            # ==========================================

            if not employee.user:

                return self.failed(
                    f"Employee "
                    f"{employee.full_name} "
                    f"does not have a user account."
                )

            # ==========================================
            # Check Existing Authority
            # ==========================================

            existing = (
                self.repository
                .find_by_department_and_employee(
                    department_id=department_id,
                    employee_id=employee_id,
                )
            )

            # ==========================================
            # Already Active
            # ==========================================

            if existing and existing.is_active:

                return self.failed(
                    f"{employee.full_name} "
                    f"is already an assignment "
                    f"authority for "
                    f"{department.department_name}."
                )

            # ==========================================
            # Restore Inactive Authority
            # ==========================================

            if existing:

                with TransactionManager():

                    existing.is_active = True

                    existing.updated_by = (
                        created_by
                    )

                    self.repository.update(
                        existing
                    )

                return self.success(
                    f"{employee.full_name} "
                    f"has been assigned as "
                    f"Problem Assignment Authority "
                    f"for "
                    f"{department.department_name}.",
                    existing,
                )

            # ==========================================
            # Create New Authority
            # ==========================================

            authority = (
                ProblemAssignmentAuthority()
            )

            authority.department_id = (
                department_id
            )

            authority.employee_id = (
                employee_id
            )

            authority.created_by = (
                created_by
            )

            authority.updated_by = (
                created_by
            )

            authority.is_active = True

            # ==========================================
            # Save
            # ==========================================

            with TransactionManager():

                self.repository.create(
                    authority
                )

            return self.success(
                f"{employee.full_name} "
                f"has been assigned as "
                f"Problem Assignment Authority "
                f"for "
                f"{department.department_name}.",
                authority,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==================================================
    # REMOVE AUTHORITY
    # ==================================================

    def remove(
        self,
        department_id,
        employee_id,
        updated_by=None,
    ):
        """
        Remove an employee's assignment authority
        from a department.

        We use soft delete by setting is_active=False.
        """

        try:

            # ==========================================
            # Find Authority
            # ==========================================

            authority = (
                self.repository
                .find_by_department_and_employee(
                    department_id=department_id,
                    employee_id=employee_id,
                )
            )

            if not authority:

                return self.failed(
                    "Assignment authority not found."
                )

            # ==========================================
            # Already Inactive
            # ==========================================

            if not authority.is_active:

                return self.failed(
                    "Assignment authority is already inactive."
                )

            # ==========================================
            # Remove
            # ==========================================

            with TransactionManager():

                authority.is_active = False

                authority.updated_by = (
                    updated_by
                )

                self.repository.update(
                    authority
                )

            return self.success(
                "Problem Assignment Authority "
                "removed successfully.",
                authority,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==================================================
    # RESTORE AUTHORITY
    # ==================================================

    def restore(
        self,
        department_id,
        employee_id,
        updated_by=None,
    ):
        """
        Restore an inactive assignment authority.
        """

        try:

            authority = (
                self.repository
                .find_by_department_and_employee(
                    department_id=department_id,
                    employee_id=employee_id,
                )
            )

            if not authority:

                return self.failed(
                    "Assignment authority not found."
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

            if not employee.is_active:

                return self.failed(
                    f"Employee "
                    f"{employee.full_name} "
                    f"is inactive."
                )

            if not employee.user:

                return self.failed(
                    f"Employee "
                    f"{employee.full_name} "
                    f"does not have a user account."
                )

            # ==========================================
            # Restore
            # ==========================================

            with TransactionManager():

                authority.is_active = True

                authority.updated_by = (
                    updated_by
                )

                self.repository.update(
                    authority
                )

            return self.success(
                "Problem Assignment Authority "
                "restored successfully.",
                authority,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==================================================
    # GET ACTIVE AUTHORITIES
    # ==================================================

    def get_active(self):

        return (
            self.repository
            .get_active()
        )

    # ==================================================
    # GET AUTHORITY COUNT
    # ==================================================

    def count_by_department(
        self,
        department_id,
    ):

        return (
            self.repository
            .count_by_department(
                department_id
            )
        )