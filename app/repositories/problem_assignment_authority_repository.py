from sqlalchemy import and_

from app.models.problem_assignment_authority import (
    ProblemAssignmentAuthority,
)

from app.repositories.base_repository import (
    BaseRepository,
)


class ProblemAssignmentAuthorityRepository(
    BaseRepository
):

    """
    Repository for Problem Assignment Authority.

    Menentukan employee yang memiliki kewenangan
    untuk melakukan assignment Problem pada
    department tertentu.
    """

    def __init__(self):

        super().__init__(
            ProblemAssignmentAuthority
        )

    # ==================================================
    # FIND BY DEPARTMENT
    # ==================================================

    def find_by_department(
        self,
        department_id,
        is_active=True,
    ):
        """
        Get all assignment authorities
        for a specific department.
        """

        query = self.model.query.filter(
            self.model.department_id == department_id
        )

        if is_active is not None:

            query = query.filter(
                self.model.is_active.is_(is_active)
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
        is_active=True,
    ):
        """
        Get all departments where the employee
        has Problem Assignment Authority.
        """

        query = self.model.query.filter(
            self.model.employee_id == employee_id
        )

        if is_active is not None:

            query = query.filter(
                self.model.is_active.is_(is_active)
            )

        return (
            query
            .order_by(
                self.model.department_id.asc()
            )
            .all()
        )

    # ==================================================
    # FIND ONE
    # ==================================================

    def find_by_department_and_employee(
        self,
        department_id,
        employee_id,
    ):
        """
        Find a specific authority assignment.
        """

        return (
            self.model.query
            .filter(
                self.model.department_id
                == department_id,

                self.model.employee_id
                == employee_id,
            )
            .first()
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
        Check whether an employee has an active
        Problem Assignment Authority for a department.
        """

        return (
            self.model.query
            .filter(
                self.model.department_id
                == department_id,

                self.model.employee_id
                == employee_id,

                self.model.is_active.is_(True),
            )
            .first()
            is not None
        )

    # ==================================================
    # GET ACTIVE AUTHORITIES
    # ==================================================

    def get_active(self):
        """
        Get all active Problem Assignment Authorities.
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
    # GET BY DEPARTMENT IDS
    # ==================================================

    def find_by_department_ids(
        self,
        department_ids,
        is_active=True,
    ):
        """
        Get authorities for multiple departments.
        """

        if not department_ids:

            return []

        query = self.model.query.filter(
            self.model.department_id.in_(
                department_ids
            )
        )

        if is_active is not None:

            query = query.filter(
                self.model.is_active.is_(is_active)
            )

        return (
            query
            .order_by(
                self.model.department_id.asc(),
                self.model.employee_id.asc(),
            )
            .all()
        )

    # ==================================================
    # GET BY EMPLOYEE IDS
    # ==================================================

    def find_by_employee_ids(
        self,
        employee_ids,
        is_active=True,
    ):
        """
        Get authorities for multiple employees.
        """

        if not employee_ids:

            return []

        query = self.model.query.filter(
            self.model.employee_id.in_(
                employee_ids
            )
        )

        if is_active is not None:

            query = query.filter(
                self.model.is_active.is_(is_active)
            )

        return (
            query
            .order_by(
                self.model.employee_id.asc(),
                self.model.department_id.asc(),
            )
            .all()
        )

    # ==================================================
    # COUNT BY DEPARTMENT
    # ==================================================

    def count_by_department(
        self,
        department_id,
    ):
        """
        Count active assignment authorities
        for a department.
        """

        return (
            self.model.query
            .filter(
                self.model.department_id
                == department_id,

                self.model.is_active.is_(True),
            )
            .count()
        )

    # ==================================================
    # COUNT BY EMPLOYEE
    # ==================================================

    def count_by_employee(
        self,
        employee_id,
    ):
        """
        Count active departments where an employee
        has assignment authority.
        """

        return (
            self.model.query
            .filter(
                self.model.employee_id
                == employee_id,

                self.model.is_active.is_(True),
            )
            .count()
        )