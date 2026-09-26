from datetime import date, datetime, time, timedelta

from dateutil.relativedelta import relativedelta

from sqlalchemy import or_

from app.extensions import db
from app.models.improvement import Improvement
from app.models.problem import Problem
from app.models.department import Department


class PublicImprovementListService:
    """
    Service untuk Public Improvement List.

    Features:
        - Search
        - Status filter
        - Department filter
        - 6 months period filter
        - Pagination
        - Department list
    """

    # =========================================================
    # GET IMPROVEMENTS
    # =========================================================

    def get_improvements(
        self,
        page=1,
        per_page=10,
        search=None,
        status=None,
        department=None,
        period=None,
    ):

        # =====================================================
        # NORMALIZE PARAMETERS
        # =====================================================

        search = (
            search.strip()
            if search
            else ""
        )

        status = (
            status.strip()
            if status
            else ""
        )

        department = (
            department.strip()
            if department
            else ""
        )

        period = (
            period.strip()
            if period
            else ""
        )

        # =====================================================
        # DATE
        # =====================================================

        today = date.today()

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today

        start_datetime = datetime.combine(
            start_date,
            time.min,
        )

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        )

        # =====================================================
        # BASE QUERY
        # =====================================================

        query = (
            db.session.query(Improvement)
            .outerjoin(
                Problem,
                Improvement.problem_id == Problem.id,
            )
            .filter(
                Improvement.is_active.is_(True),
            )
        )

        # =====================================================
        # PERIOD FILTER
        # =====================================================

        if period == "6_months":

            query = query.filter(
                Improvement.created_at >= start_datetime,
                Improvement.created_at < end_datetime,
            )

        # =====================================================
        # SEARCH
        # =====================================================

        if search:

            keyword = f"%{search}%"

            query = query.filter(
                or_(
                    Improvement.improvement_no.ilike(
                        keyword
                    ),
                    Improvement.title.ilike(
                        keyword
                    ),
                    Improvement.description.ilike(
                        keyword
                    ),
                )
            )

        # =====================================================
        # STATUS FILTER
        # =====================================================

        if status == "Open":

            query = query.filter(
                Improvement.implementation_result.is_(None),
                Improvement.verification_result.is_(None),
                Improvement.approved_date.is_(None),
            )

        elif status == "Implemented":

            query = query.filter(
                Improvement.implementation_result.isnot(None),
                Improvement.verification_result.is_(None),
                Improvement.approved_date.is_(None),
            )

        elif status == "Verified":

            query = query.filter(
                Improvement.verification_result.isnot(None),
                Improvement.approved_date.is_(None),
            )

        elif status == "Completed":

            query = query.filter(
                Improvement.approved_date.isnot(None)
            )

        # =====================================================
        # DEPARTMENT FILTER
        # =====================================================

        if department:

            try:

                department_id = int(
                    department
                )

                query = query.filter(
                    Problem.department_id
                    == department_id
                )

            except (
                TypeError,
                ValueError,
            ):

                department = ""

        # =====================================================
        # ORDER
        # =====================================================

        query = query.order_by(
            Improvement.created_at.desc(),
            Improvement.id.desc(),
        )

        # =====================================================
        # PAGINATION
        # =====================================================

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

        # =====================================================
        # BUILD IMPROVEMENT LIST
        # =====================================================

        improvements = []

        for item in pagination.items:

            # -------------------------------------------------
            # RELATED PROBLEM
            # -------------------------------------------------

            problem = item.problem

            # -------------------------------------------------
            # DEPARTMENT
            # -------------------------------------------------

            department_object = (
                problem.department
                if problem
                else None
            )

            if department_object:

                department_name = (
                    department_object.department_name
                )

            else:

                department_name = "-"

            # -------------------------------------------------
            # STATUS
            # -------------------------------------------------

            if item.approved_date:

                improvement_status = "Completed"

            elif item.verification_result:

                improvement_status = "Verified"

            elif item.implementation_result:

                improvement_status = "Implemented"

            else:

                improvement_status = "Open"

            # -------------------------------------------------
            # RESULT
            # -------------------------------------------------

            improvements.append(
                {
                    "id": item.id,

                    "improvement_no": (
                        item.improvement_no
                    ),

                    "title": (
                        item.title
                    ),

                    "description": (
                        item.description
                    ),

                    "problem_no": (
                        problem.problem_no
                        if problem
                        else "-"
                    ),

                    "department": (
                        department_name
                    ),

                    "department_id": (
                        problem.department_id
                        if problem
                        else None
                    ),

                    "status": (
                        improvement_status
                    ),

                    "created_at": (
                        item.created_at
                    ),

                    "approved_date": (
                        item.approved_date
                    ),

                    "improvement_cost": float(
                        item.improvement_cost or 0
                    ),

                    "estimated_cost_saving": float(
                        item.estimated_cost_saving or 0
                    ),

                    "estimated_benefit": float(
                        item.estimated_benefit or 0
                    ),

                    "estimated_time_saving": float(
                        item.estimated_time_saving or 0
                    ),
                }
            )

        # =====================================================
        # DEPARTMENT LIST
        # =====================================================

        departments = (
            db.session.query(Department)
            .filter(
                Department.is_active.is_(True)
            )
            .order_by(
                Department.department_name.asc()
            )
            .all()
        )

        # =====================================================
        # RETURN
        # =====================================================

        return {
            "improvements": improvements,

            "pagination": pagination,

            "search": search,

            "status": status,

            "department": department,

            "departments": departments,

            "period": period,

            "period_start": (
                start_date
                if period == "6_months"
                else None
            ),

            "period_end": (
                end_date
                if period == "6_months"
                else None
            ),
        }