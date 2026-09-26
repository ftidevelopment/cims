from datetime import datetime

from app.models.problem import Problem
from app.repositories.base_repository import BaseRepository


class ProblemRepository(BaseRepository):

    searchable_fields = [
        Problem.problem_no,
        Problem.title,
        Problem.problem_location,
    ]

    sortable_fields = {
        "problem_no": Problem.problem_no,
        "problem_date": Problem.problem_date,
        "priority": Problem.priority,
        "status": Problem.status,
        "title": Problem.title,
        "created_at": Problem.created_at,
    }

    def __init__(self):
        super().__init__(Problem)

    # ==========================================
    # Query
    # ==========================================

    def get_query(
        self,
        keyword=None,
        status=None,
        priority=None,
        department_id=None,
        date_from=None,
        date_to=None,
        created_by=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):

        query = super().get_query(
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # ==========================================
        # Status
        # ==========================================

        if status:

            query = query.filter(
                Problem.status == status
            )

        # ==========================================
        # Priority
        # ==========================================

        if priority:

            query = query.filter(
                Problem.priority == priority
            )

        # ==========================================
        # Department
        # ==========================================

        if department_id:

            query = query.filter(
                Problem.department_id == department_id
            )

        # ==========================================
        # Created By
        # ==========================================

        if created_by:

            query = query.filter(
                Problem.created_by == created_by
            )

        # ==========================================
        # Date From
        # ==========================================

        if date_from:

            try:

                date_from_value = datetime.strptime(
                    date_from,
                    "%Y-%m-%d",
                ).date()

                query = query.filter(
                    Problem.problem_date
                    >= date_from_value
                )

            except ValueError:

                pass

        # ==========================================
        # Date To
        # ==========================================

        if date_to:

            try:

                date_to_value = datetime.strptime(
                    date_to,
                    "%Y-%m-%d",
                ).date()

                query = query.filter(
                    Problem.problem_date
                    <= date_to_value
                )

            except ValueError:

                pass

        return query

    # ==========================================
    # List
    # ==========================================

    def get_all(
        self,
        keyword=None,
        status=None,
        priority=None,
        department_id=None,
        date_from=None,
        date_to=None,
        created_by=None,
        is_active=True,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="asc",
    ):

        query = self.get_query(
            keyword=keyword,
            status=status,
            priority=priority,
            department_id=department_id,
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

    # ==========================================
    # Find
    # ==========================================

    def get_by_problem_no(self, problem_no):

        return self.get_first_by(
            problem_no=problem_no
        )

    # ==========================================
    # Auto Number
    # ==========================================

    def get_last_problem_no(self, prefix):

        return self.get_last_by(
            self.model.problem_no,
            prefix
        )