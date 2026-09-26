from app.models.improvement_assignment_authority import (
    ImprovementAssignmentAuthority,
)

from app.repositories.base_repository import (
    BaseRepository,
)


class ImprovementAssignmentAuthorityRepository(
    BaseRepository
):

    def __init__(self):

        super().__init__(
            ImprovementAssignmentAuthority
        )

    # ==================================================
    # FIND BY DEPARTMENT
    # ==================================================

    def find_by_department(
        self,
        department_id,
        active_only=True,
    ):
        """
        Get Improvement Assignment Authorities
        for a specific department.
        """

        query = (
            self.model.query
            .filter(
                self.model.department_id
                == department_id
            )
        )

        if active_only:

            query = query.filter(
                self.model.is_active.is_(True)
            )

        return (
            query
            .order_by(
                self.model.employee_id.asc()
            )
            .all()
        )

    # ==================================================
    # FIND BY EMPLOYEE
    # ==================================================

    def find_by_employee(
        self,
        employee_id,
        active_only=True,
    ):
        """
        Get all departments where the employee
        has Improvement Assignment Authority.
        """

        query = (
            self.model.query
            .filter(
                self.model.employee_id
                == employee_id
            )
        )

        if active_only:

            query = query.filter(
                self.model.is_active.is_(True)
            )

        return (
            query
            .order_by(
                self.model.department_id.asc()
            )
            .all()
        )

    # ==================================================
    # FIND SPECIFIC AUTHORITY
    # ==================================================

    def find_by_department_and_employee(
        self,
        department_id,
        employee_id,
        active_only=True,
    ):
        """
        Find authority for a specific
        department + employee combination.
        """

        query = (
            self.model.query
            .filter(
                self.model.department_id
                == department_id
            )
            .filter(
                self.model.employee_id
                == employee_id
            )
        )

        if active_only:

            query = query.filter(
                self.model.is_active.is_(True)
            )

        return query.first()

    # ==================================================
    # CHECK AUTHORITY
    # ==================================================

    def has_authority(
        self,
        department_id,
        employee_id,
    ):
        """
        Return True when employee has an active
        Improvement Assignment Authority for
        the specified department.
        """

        return (
            self.model.query
            .filter(
                self.model.department_id
                == department_id
            )
            .filter(
                self.model.employee_id
                == employee_id
            )
            .filter(
                self.model.is_active.is_(True)
            )
            .first()
            is not None
        )

    # ==================================================
    # FIND ACTIVE AUTHORITIES
    # ==================================================

    def get_active(self):
        """
        Get all active Improvement Assignment
        Authorities.
        """

        return (
            self.model.query
            .filter(
                self.model.is_active.is_(True)
            )
            .order_by(
                self.model.department_id.asc(),
                self.model.employee_id.asc(),
            )
            .all()
        )

    # ==================================================
    # FIND ALL AUTHORITIES
    # ==================================================

    def get_all_authorities(self):
        """
        Get all Improvement Assignment Authorities,
        including inactive records.
        """

        return (
            self.model.query
            .order_by(
                self.model.department_id.asc(),
                self.model.employee_id.asc(),
            )
            .all()
        )

    # ==================================================
    # DEACTIVATE AUTHORITY
    # ==================================================

    def deactivate(
        self,
        authority,
        updated_by=None,
    ):
        """
        Soft delete / revoke authority.
        """

        authority.is_active = False

        if updated_by is not None:

            authority.updated_by = updated_by

        return self.update(
            authority
        )

    # ==================================================
    # REACTIVATE AUTHORITY
    # ==================================================

    def reactivate(
        self,
        authority,
        updated_by=None,
    ):
        """
        Reactivate an existing authority.
        """

        authority.is_active = True

        if updated_by is not None:

            authority.updated_by = updated_by

        return self.update(
            authority
        )