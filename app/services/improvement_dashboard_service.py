from datetime import date

from dateutil.relativedelta import relativedelta

from sqlalchemy import (
    func,
    or_
)

from app.extensions import db

from app.models.improvement import Improvement
from app.models.problem import Problem
from app.models.department import Department


class ImprovementDashboardService:

    # ==================================================
    # PUBLIC IMPROVEMENT DASHBOARD
    # ==================================================

    def get_dashboard(
        self,
        page=1,
        per_page=10,
        search=None,
        status=None,
        department=None
    ):

        today = date.today()

        # ==================================================
        # Last 6 Months
        # ==================================================

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today

        # ==================================================
        # Base Query
        # ==================================================

        base_query = (
            db.session.query(Improvement)
            .join(
                Problem,
                Improvement.problem_id == Problem.id
            )
            .filter(
                Improvement.is_active.is_(True),
                Problem.is_active.is_(True)
            )
        )

        # ==================================================
        # TOTAL IMPROVEMENT
        # ==================================================

        total_improvement = (
            base_query.count()
        )

        # ==================================================
        # COMPLETED IMPROVEMENT
        #
        # Based on approved_date
        # ==================================================

        completed_improvement = (
            base_query
            .filter(
                Improvement.approved_date.isnot(None)
            )
            .count()
        )

        # ==================================================
        # OPEN / ON PROGRESS
        #
        # approved_date is NULL
        # ==================================================

        open_improvement = (
            base_query
            .filter(
                Improvement.approved_date.is_(None)
            )
            .count()
        )

        # ==================================================
        # FINANCIAL SUMMARY
        # ==================================================

        financial_row = (
            base_query
            .with_entities(
                func.coalesce(
                    func.sum(
                        Improvement.improvement_cost
                    ),
                    0
                ).label("total_cost"),

                func.coalesce(
                    func.sum(
                        Improvement.estimated_cost_saving
                    ),
                    0
                ).label("total_saving"),

                func.coalesce(
                    func.sum(
                        Improvement.estimated_benefit
                    ),
                    0
                ).label("total_benefit"),

                func.coalesce(
                    func.sum(
                        Improvement.estimated_time_saving
                    ),
                    0
                ).label("total_time_saving")
            )
            .first()
        )

        total_cost = float(
            financial_row.total_cost or 0
        )

        total_saving = float(
            financial_row.total_saving or 0
        )

        total_benefit = float(
            financial_row.total_benefit or 0
        )

        total_time_saving = (
            financial_row.total_time_saving or 0
        )

        net_benefit = (
            total_benefit
            - total_cost
        )

        # ==================================================
        # IMPROVEMENT TREND
        # Last 6 Months
        #
        # Use created_at because Improvement
        # does not have improvement_date.
        # ==================================================

        trend_rows = (
            base_query
            .with_entities(
                func.year(
                    Improvement.created_at
                ).label("year"),

                func.month(
                    Improvement.created_at
                ).label("month"),

                func.count(
                    Improvement.id
                ).label("total")
            )
            .filter(
                Improvement.created_at >= start_date,
                Improvement.created_at <= end_date
            )
            .group_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                )
            )
            .order_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                )
            )
            .all()
        )

        trend_map = {
            (
                row.year,
                row.month
            ): row.total
            for row in trend_rows
        }

        improvement_trend = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month
            )

            improvement_trend.append({

                "year": current_month.year,

                "month": current_month.month,

                "label": current_month.strftime(
                    "%b %Y"
                ),

                "total": trend_map.get(
                    key,
                    0
                )
            })

            current_month += relativedelta(
                months=1
            )

        # ==================================================
        # SAVING TREND
        # ==================================================

        saving_rows = (
            base_query
            .with_entities(
                func.year(
                    Improvement.created_at
                ).label("year"),

                func.month(
                    Improvement.created_at
                ).label("month"),

                func.coalesce(
                    func.sum(
                        Improvement.estimated_cost_saving
                    ),
                    0
                ).label("saving")
            )
            .filter(
                Improvement.created_at >= start_date,
                Improvement.created_at <= end_date
            )
            .group_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                )
            )
            .order_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                )
            )
            .all()
        )

        saving_map = {
            (
                row.year,
                row.month
            ): float(row.saving or 0)
            for row in saving_rows
        }

        saving_trend = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month
            )

            saving_trend.append({

                "year": current_month.year,

                "month": current_month.month,

                "label": current_month.strftime(
                    "%b %Y"
                ),

                "saving": saving_map.get(
                    key,
                    0
                )
            })

            current_month += relativedelta(
                months=1
            )

        # ==================================================
        # COST TREND
        # ==================================================

        cost_rows = (
            base_query
            .with_entities(
                func.year(
                    Improvement.created_at
                ).label("year"),

                func.month(
                    Improvement.created_at
                ).label("month"),

                func.coalesce(
                    func.sum(
                        Improvement.improvement_cost
                    ),
                    0
                ).label("cost")
            )
            .filter(
                Improvement.created_at >= start_date,
                Improvement.created_at <= end_date
            )
            .group_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                )
            )
            .order_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                )
            )
            .all()
        )

        cost_map = {
            (
                row.year,
                row.month
            ): float(row.cost or 0)
            for row in cost_rows
        }

        cost_trend = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month
            )

            cost_trend.append({

                "year": current_month.year,

                "month": current_month.month,

                "label": current_month.strftime(
                    "%b %Y"
                ),

                "cost": cost_map.get(
                    key,
                    0
                )
            })

            current_month += relativedelta(
                months=1
            )

        # ==================================================
        # IMPROVEMENT BY DEPARTMENT
        # ==================================================

        department_rows = (
            base_query
            .join(
                Department,
                Problem.department_id == Department.id
            )
            .with_entities(
                Department.department_name.label(
                    "department_name"
                ),

                func.count(
                    Improvement.id
                ).label("total")
            )
            .group_by(
                Department.id,
                Department.department_name
            )
            .order_by(
                func.count(
                    Improvement.id
                ).desc()
            )
            .all()
        )

        department_data = []

        for row in department_rows:

            department_data.append({

                "department": row.department_name,

                "total": row.total

            })

        # ==================================================
        # DEPARTMENT LIST
        #
        # Used for Department Filter
        # ==================================================

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

        # ==================================================
        # IMPROVEMENT LIST
        # ==================================================

        query = (
            db.session.query(Improvement)
            .join(
                Problem,
                Improvement.problem_id == Problem.id
            )
            .filter(
                Improvement.is_active.is_(True),
                Problem.is_active.is_(True)
            )
        )

        # ==================================================
        # SEARCH
        # ==================================================

        if search:

            keyword = (
                f"%{search.strip()}%"
            )

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
                    )

                )
            )

        # ==================================================
        # STATUS FILTER
        # ==================================================

        if status:

            if status == "Completed":

                query = query.filter(
                    Improvement.approved_date.isnot(None)
                )

            elif status == "Verified":

                query = query.filter(
                    Improvement.approved_date.is_(None),
                    Improvement.verification_result.isnot(None)
                )

            elif status == "Implemented":

                query = query.filter(
                    Improvement.approved_date.is_(None),
                    Improvement.verification_result.is_(None),
                    Improvement.implementation_result.isnot(None)
                )

            elif status == "Open":

                query = query.filter(
                    Improvement.approved_date.is_(None),
                    Improvement.verification_result.is_(None),
                    Improvement.implementation_result.is_(None)
                )

        # ==================================================
        # DEPARTMENT FILTER
        # ==================================================

        if department:

            try:

                department_id = int(
                    department
                )

                query = query.filter(
                    Problem.department_id == department_id
                )

            except (
                TypeError,
                ValueError
            ):

                pass

        # ==================================================
        # ORDER
        # ==================================================

        query = query.order_by(
            Improvement.created_at.desc(),
            Improvement.id.desc()
        )

        # ==================================================
        # PAGINATION
        # ==================================================

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        improvements = []

        for item in pagination.items:

            problem = item.problem

            department_obj = (
                problem.department
                if problem
                else None
            )

            # ----------------------------------------------
            # STATUS
            # ----------------------------------------------

            if item.approved_date:

                item_status = "Completed"

            elif item.verification_result:

                item_status = "Verified"

            elif item.implementation_result:

                item_status = "Implemented"

            else:

                item_status = "Open"

            improvements.append({

                "id": item.id,

                "improvement_no": (
                    item.improvement_no
                ),

                "title": item.title,

                "problem_no": (
                    problem.problem_no
                    if problem
                    else "-"
                ),

                "department": (
                    department_obj.department_name
                    if department_obj
                    else "-"
                ),

                "status": item_status,

                "created_at": item.created_at,

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

                "estimated_time_saving": (
                    item.estimated_time_saving or 0
                )

            })

        # ==================================================
        # RETURN DASHBOARD DATA
        # ==================================================

        return {

            "period": {

                "start_date": start_date,

                "end_date": end_date

            },

            "summary": {

                "total": total_improvement,

                "completed": (
                    completed_improvement
                ),

                "open": open_improvement,

                "total_cost": total_cost,

                "total_saving": total_saving,

                "total_benefit": total_benefit,

                "net_benefit": net_benefit,

                "total_time_saving": (
                    total_time_saving
                )

            },

            "trend": improvement_trend,

            "saving_trend": saving_trend,

            "cost_trend": cost_trend,

            "by_department": department_data,

            "improvements": improvements,

            "pagination": pagination,

            "search": search or "",

            "status": status or "",

            "department": department or "",

            "departments": departments

        }

    # ==================================================
    # GET IMPROVEMENT DETAIL
    # ==================================================

    def get_improvement_detail(
        self,
        improvement_id
    ):

        improvement = (
            db.session.query(Improvement)
            .join(
                Problem,
                Improvement.problem_id == Problem.id
            )
            .filter(
                Improvement.id == improvement_id,
                Improvement.is_active.is_(True),
                Problem.is_active.is_(True)
            )
            .first()
        )

        return improvement

    # ==================================================
    # CALCULATE BENEFIT
    # ==================================================

    def calculate_benefit(
        self,
        improvement_id
    ):

        improvement = (
            db.session.query(Improvement)
            .filter(
                Improvement.id == improvement_id,
                Improvement.is_active.is_(True)
            )
            .first()
        )

        if not improvement:

            return {

                "improvement_cost": 0,

                "estimated_cost_saving": 0,

                "estimated_time_saving": 0,

                "estimated_benefit": 0,

                "net_benefit": 0,

                "roi": 0

            }

        cost = float(
            improvement.improvement_cost or 0
        )

        cost_saving = float(
            improvement.estimated_cost_saving or 0
        )

        time_saving = (
            improvement.estimated_time_saving or 0
        )

        benefit = float(
            improvement.estimated_benefit or 0
        )

        net_benefit = (
            benefit
            - cost
        )

        roi = 0

        if cost > 0:

            roi = (
                net_benefit
                / cost
                * 100
            )

        return {

            "improvement_cost": cost,

            "estimated_cost_saving": cost_saving,

            "estimated_time_saving": time_saving,

            "estimated_benefit": benefit,

            "net_benefit": net_benefit,

            "roi": roi

        }