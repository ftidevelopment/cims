from app.models.improvement_pic import (
    ImprovementPIC,
)

from app.models.improvement import (
    Improvement,
)

from app.repositories.base_repository import (
    BaseRepository,
)

from app.extensions import db


class ImprovementPICRepository(
    BaseRepository
):

    def __init__(self):

        super().__init__(
            ImprovementPIC
        )

    # ==================================================
    # GET BY IMPROVEMENT
    # ==================================================

    def find_by_improvement_id(
        self,
        improvement_id,
        active_only=True,
    ):
        """
        Get all PICs assigned to an Improvement.
        """

        query = (
            self.model.query
            .filter(
                self.model.improvement_id
                == improvement_id
            )
        )

        if active_only:

            query = query.filter(
                self.model.is_active.is_(True)
            )

        return (
            query
            .order_by(
                self.model.is_leader.desc(),
                self.model.id.asc(),
            )
            .all()
        )

    # ==================================================
    # GET LEADER
    # ==================================================

    def get_leader(
        self,
        improvement_id,
        active_only=True,
    ):
        """
        Get the Leader PIC of an Improvement.
        """

        query = (
            self.model.query
            .filter(
                self.model.improvement_id
                == improvement_id
            )
            .filter(
                self.model.is_leader.is_(True)
            )
        )

        if active_only:

            query = query.filter(
                self.model.is_active.is_(True)
            )

        return query.first()

    # ==================================================
    # GET BY EMPLOYEE
    # ==================================================

    def find_by_employee_id(
        self,
        employee_id,
        active_only=True,
    ):
        """
        Get all Improvements where the employee
        is assigned as PIC.
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
                self.model.improvement_id.desc()
            )
            .all()
        )

    # ==================================================
    # GET SPECIFIC PIC
    # ==================================================

    def find_by_improvement_and_employee(
        self,
        improvement_id,
        employee_id,
        active_only=True,
    ):
        """
        Find a specific employee assigned as PIC
        for a specific Improvement.
        """

        query = (
            self.model.query
            .filter(
                self.model.improvement_id
                == improvement_id
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
    # CHECK PIC
    # ==================================================

    def is_pic(
        self,
        improvement_id,
        employee_id,
    ):
        """
        Check whether an employee is an active
        PIC of an Improvement.
        """

        return (
            self.model.query
            .filter(
                self.model.improvement_id
                == improvement_id
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
    # DELETE BY IMPROVEMENT
    # ==================================================

    def delete_by_improvement_id(
        self,
        improvement_id,
    ):
        """
        Hard delete all PIC records
        belonging to an Improvement.
        """

        improvement_pics = (
            self.model.query
            .filter(
                self.model.improvement_id
                == improvement_id
            )
            .all()
        )

        for improvement_pic in improvement_pics:

            db.session.delete(
                improvement_pic
            )

        return improvement_pics

    # ==================================================
    # DELETE BY PROBLEM
    # ==================================================

    def delete_by_problem_id(
        self,
        problem_id,
    ):
        """
        Hard delete all Improvement PIC records
        belonging to Improvements created from
        the specified Problem.

        Example:

        Problem
            ├── Improvement 1
            │      ├── PIC A
            │      └── PIC B
            │
            └── Improvement 2
                   ├── PIC A
                   └── PIC B

        All PIC records above will be deleted.
        """

        improvement_pics = (
            self.model.query
            .join(
                Improvement,
                Improvement.id
                == self.model.improvement_id
            )
            .filter(
                Improvement.problem_id
                == problem_id
            )
            .all()
        )

        for improvement_pic in improvement_pics:

            db.session.delete(
                improvement_pic
            )

        return improvement_pics

    # ==================================================
    # DEACTIVATE PIC
    # ==================================================

    def deactivate(
        self,
        pic,
        updated_by=None,
    ):
        """
        Deactivate an Improvement PIC.
        """

        pic.is_active = False

        if updated_by is not None:

            pic.updated_by = (
                updated_by
            )

        return self.update(
            pic
        )

    # ==================================================
    # REACTIVATE PIC
    # ==================================================

    def reactivate(
        self,
        pic,
        updated_by=None,
    ):
        """
        Reactivate an Improvement PIC.
        """

        pic.is_active = True

        if updated_by is not None:

            pic.updated_by = (
                updated_by
            )

        return self.update(
            pic
        )