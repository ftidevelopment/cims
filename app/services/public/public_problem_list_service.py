from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy import or_

from app.extensions import db
from app.models.problem import Problem
from app.core.choices.problem import (
    ProblemPriority,
    ProblemStatus,
)


class PublicProblemListService:

    def get_problems(
        self,
        page=1,
        per_page=10,
        search=None,
        status=None,
        priority=None,
        department_id=None,
        open_only=False,
        period=None,
        aging=None,
    ):
        today = date.today()

        # =========================================================
        # LAST 6 MONTHS
        # =========================================================

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today

        # =========================================================
        # OPEN STATUS
        # =========================================================

        open_statuses = [
            ProblemStatus.OPEN,
            ProblemStatus.IN_PROGRESS,
        ]

        # =========================================================
        # BASE QUERY
        # =========================================================

        query = (
            db.session.query(Problem)
            .filter(
                Problem.is_active.is_(True)
            )
        )

        # =========================================================
        # STATUS FILTER
        # =========================================================

        if status:

            query = query.filter(
                Problem.status == status
            )

        elif open_only:

            query = query.filter(
                Problem.status.in_(open_statuses)
            )

        # =========================================================
        # PERIOD FILTER
        # =========================================================

        if period == "6_months":

            query = query.filter(
                Problem.problem_date >= start_date,
                Problem.problem_date <= end_date,
            )

        # =========================================================
        # SEARCH
        # =========================================================

        if search:

            keyword = f"%{search.strip()}%"

            query = query.filter(
                or_(
                    Problem.problem_no.ilike(keyword),
                    Problem.title.ilike(keyword),
                    Problem.description.ilike(keyword),
                )
            )

        # =========================================================
        # PRIORITY FILTER
        # =========================================================

        if priority:

            query = query.filter(
                Problem.priority == priority
            )

        # =========================================================
        # DEPARTMENT FILTER
        # =========================================================

        if department_id:

            try:

                department_id = int(
                    department_id
                )

                query = query.filter(
                    Problem.department_id
                    == department_id
                )

            except (
                TypeError,
                ValueError,
            ):

                department_id = ""

        # =========================================================
        # AGING FILTER
        #
        # Aging applies only to:
        # Open + In Progress
        #
        # Aging is calculated from Problem Date
        # =========================================================

        if aging:

            query = query.filter(
                Problem.status.in_(open_statuses)
            )

            aging_problem_ids = []

            aging_rows = (
                db.session.query(Problem)
                .filter(
                    Problem.is_active.is_(True),
                    Problem.status.in_(open_statuses),
                )
                .all()
            )

            for problem in aging_rows:

                if problem.problem_date:

                    aging_days = (
                        today
                        - problem.problem_date
                    ).days

                else:

                    aging_days = 0

                # ---------------------------------------------
                # 0 - 7 DAYS
                # ---------------------------------------------

                if aging == "0_7":

                    matched = (
                        aging_days <= 7
                    )

                # ---------------------------------------------
                # 8 - 14 DAYS
                # ---------------------------------------------

                elif aging == "8_14":

                    matched = (
                        aging_days >= 8
                        and aging_days <= 14
                    )

                # ---------------------------------------------
                # 15 - 30 DAYS
                # ---------------------------------------------

                elif aging == "15_30":

                    matched = (
                        aging_days >= 15
                        and aging_days <= 30
                    )

                # ---------------------------------------------
                # 31 - 60 DAYS
                # ---------------------------------------------

                elif aging == "31_60":

                    matched = (
                        aging_days >= 31
                        and aging_days <= 60
                    )

                # ---------------------------------------------
                # MORE THAN 60 DAYS
                # ---------------------------------------------

                elif aging == "over_60":

                    matched = (
                        aging_days > 60
                    )

                else:

                    matched = False

                if matched:

                    aging_problem_ids.append(
                        problem.id
                    )

            # =====================================================
            # APPLY AGING IDS
            # =====================================================

            if aging_problem_ids:

                query = query.filter(
                    Problem.id.in_(
                        aging_problem_ids
                    )
                )

            else:

                # Return empty result
                query = query.filter(
                    Problem.id == -1
                )

        # =========================================================
        # ORDER
        # =========================================================

        query = query.order_by(
            Problem.problem_date.desc(),
            Problem.id.desc(),
        )

        # =========================================================
        # PAGINATION
        # =========================================================

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

        # =========================================================
        # PREPARE RESULT
        # =========================================================

        problems = []

        for problem in pagination.items:

            # -----------------------------------------------------
            # AGING
            # -----------------------------------------------------

            if (
                problem.status in open_statuses
                and problem.problem_date
            ):

                aging_days = (
                    today
                    - problem.problem_date
                ).days

            elif problem.status in open_statuses:

                aging_days = 0

            else:

                aging_days = None

            # -----------------------------------------------------
            # DEPARTMENT
            # -----------------------------------------------------

            if problem.department:

                department_name = (
                    problem.department.department_name
                )

            else:

                department_name = "-"

            # -----------------------------------------------------
            # RESULT
            # -----------------------------------------------------

            problems.append(
                {
                    "id": problem.id,

                    "problem_no": (
                        problem.problem_no
                    ),

                    "problem_date": (
                        problem.problem_date
                    ),

                    "title": (
                        problem.title
                    ),

                    "department": (
                        department_name
                    ),

                    "department_id": getattr(
                        problem,
                        "department_id",
                        None,
                    ),

                    "priority": (
                        problem.priority
                    ),

                    "status": (
                        problem.status
                    ),

                    "aging_days": (
                        aging_days
                    ),

                    "loss_cost": float(
                        problem.loss_cost or 0
                    ),
                }
            )

        # =========================================================
        # RETURN
        # =========================================================

        return {
            "problems": problems,

            "pagination": pagination,

            "search": search or "",

            "status": status or "",

            "priority": priority or "",

            "department_id": (
                department_id
                if department_id
                else ""
            ),

            "open_only": (
                open_only
            ),

            "period": (
                period or ""
            ),

            "aging": (
                aging or ""
            ),

            "period_start": (
                start_date
            ),

            "period_end": (
                end_date
            ),
        }