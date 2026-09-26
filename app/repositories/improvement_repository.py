from app.models.improvement import Improvement
from datetime import datetime, timedelta
from app.repositories.base_repository import (
    BaseRepository,
)


class ImprovementRepository(BaseRepository):

    def __init__(self):

        super().__init__(
            Improvement
        )

        # ==================================================
        # Searchable Fields
        # ==================================================

        self.searchable_fields = [
            Improvement.improvement_no,
            Improvement.title,
            Improvement.description,
        ]

        # ==================================================
        # Sortable Fields
        # ==================================================

        self.sortable_fields = {

            "id": (
                Improvement.id
            ),

            "improvement_no": (
                Improvement.improvement_no
            ),

            "title": (
                Improvement.title
            ),

            "problem_id": (
                Improvement.problem_id
            ),

            "owner": (
                Improvement.owner_employee_id
            ),

            "improvement_cost": (
                Improvement.improvement_cost
            ),

            "estimated_benefit": (
                Improvement.estimated_benefit
            ),

            "approved_by": (
                Improvement.approved_by_employee_id
            ),

            "approved_date": (
                Improvement.approved_date
            ),

            "created_at": (
                Improvement.created_at
            ),

            "updated_at": (
                Improvement.updated_at
            ),
        }

    def get_query(
        self,
        keyword=None,
        approval=None,
        date_from=None,
        date_to=None,
        created_by=None,
        is_active=True,
        sort_by=None,
        sort_order="desc",
    ):

        # Get base query
        query = super().get_query(
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # ==================================================
        # OWNER FILTER
        # ==================================================

        if created_by:

            query = query.filter(
                Improvement.owner_employee_id == created_by
            )

        # ==================================================
        # Approval Filter
        # ==================================================

        if approval == "approved":

            query = query.filter(
                Improvement.approved_date.isnot(None)
            )

        elif approval == "verified":

            query = query.filter(
                Improvement.approved_date.is_(None),
                Improvement.verification_result.isnot(None)
            )

        elif approval == "implemented":

            query = query.filter(
                Improvement.approved_date.is_(None),
                Improvement.verification_result.is_(None),
                Improvement.implementation_result.isnot(None)
            )

        elif approval == "open":

            query = query.filter(
                Improvement.approved_date.is_(None),
                Improvement.verification_result.is_(None),
                Improvement.implementation_result.is_(None)
            )

        # ==================================================
        # DATE FILTER
        # ==================================================

        if date_from:

            try:

                date_from_value = datetime.strptime(
                    date_from,
                    "%Y-%m-%d"
                )

                query = query.filter(
                    Improvement.created_at >= date_from_value
                )

            except ValueError:

                pass

        if date_to:

            try:

                date_to_value = datetime.strptime(
                    date_to,
                    "%Y-%m-%d"
                )

                date_to_exclusive = (
                    date_to_value
                    + timedelta(days=1)
                )

                query = query.filter(
                    Improvement.created_at < date_to_exclusive
                )

            except ValueError:

                pass

        return query

    # ==================================================
    # GET ALL
    # ==================================================

    def get_all(
        self,
        keyword="",
        approval="",
        date_from="",
        date_to="",
        created_by=None,
        is_active=True,
        page=1,
        per_page=10,
        sort_by="id",
        sort_order="desc",
    ):

        query = self.get_query(
                keyword=keyword,
                approval=approval,
                date_from=date_from,
                date_to=date_to,
                created_by=created_by,
                is_active=is_active,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
    # ==================================================
    # FIND BY PROBLEM
    # ==================================================

    def find_by_problem_id(
        self,
        problem_id,
    ):

        return (
            self.model.query
            .filter(
                self.model.problem_id
                == problem_id
            )
            .filter(
                self.model.is_active.is_(True)
            )
            .order_by(
                self.model.id.desc()
            )
            .all()
        )

    # ==================================================
    # FIND BY IMPROVEMENT NO
    # ==================================================

    def find_by_improvement_no(
        self,
        improvement_no,
    ):

        return (
            self.model.query
            .filter(
                self.model.improvement_no
                == improvement_no
            )
            .first()
        )

    # ==================================================
    # FIND BY OWNER
    # ==================================================

    def find_by_owner(
        self,
        employee_id,
    ):

        return (
            self.model.query
            .filter(
                self.model.owner_employee_id
                == employee_id
            )
            .filter(
                self.model.is_active.is_(True)
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ==================================================
    # FIND BY APPROVER
    # ==================================================

    def find_by_approver(
        self,
        employee_id,
    ):

        return (
            self.model.query
            .filter(
                self.model.approved_by_employee_id
                == employee_id
            )
            .filter(
                self.model.is_active.is_(True)
            )
            .order_by(
                self.model.approved_date.desc()
            )
            .all()
        )

    # ==================================================
    # FIND UNAPPROVED
    # ==================================================

    def find_unapproved(self):

        return (
            self.model.query
            .filter(
                self.model.approved_by_employee_id
                .is_(None)
            )
            .filter(
                self.model.is_active.is_(True)
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ==================================================
    # FIND APPROVED
    # ==================================================

    def find_approved(self):

        return (
            self.model.query
            .filter(
                self.model.approved_by_employee_id
                .isnot(None)
            )
            .filter(
                self.model.is_active.is_(True)
            )
            .order_by(
                self.model.approved_date.desc()
            )
            .all()
        )

    # ==================================================
    # FIND BY OWNER AND PROBLEM
    # ==================================================

    def find_by_owner_and_problem(
        self,
        employee_id,
        problem_id,
    ):

        return (
            self.model.query
            .filter(
                self.model.owner_employee_id
                == employee_id
            )
            .filter(
                self.model.problem_id
                == problem_id
            )
            .filter(
                self.model.is_active.is_(True)
            )
            .all()
        )

    # ==================================================
    # GET OWNER
    # ==================================================

    def get_owner(
        self,
        improvement_id,
    ):

        improvement = self.get_by_id(
            improvement_id
        )

        if not improvement:
            return None

        return improvement.owner

    # ==================================================
    # GET APPROVER
    # ==================================================

    def get_approver(
        self,
        improvement_id,
    ):

        improvement = self.get_by_id(
            improvement_id
        )

        if not improvement:
            return None

        return improvement.approved_by