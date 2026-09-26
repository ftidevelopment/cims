from datetime import date, datetime, time, timedelta

from dateutil.relativedelta import relativedelta

from sqlalchemy import func

from app.extensions import db
from app.models.improvement import Improvement
from app.models.problem import Problem
from app.models.department import Department


class PublicImprovementDashboardService:
    """
    Public Improvement Dashboard Service.

    Dashboard period:
        Last 6 months.

    Status:
        Open
        Implemented
        Verified
        Completed

    Financial:
        Improvement Cost
        Cost Saving
        Estimated Benefit
        Net Benefit
        Time Saving
    """

    # =========================================================
    # DASHBOARD
    # =========================================================

    def get_dashboard(self):

        today = date.today()

        # =====================================================
        # LAST 6 MONTHS
        # =====================================================

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today

        # -----------------------------------------------------
        # Datetime boundary
        # -----------------------------------------------------

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

        active_query = (
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
        # PERIOD QUERY
        # =====================================================

        period_query = (
            active_query
            .filter(
                Improvement.created_at >= start_datetime,
                Improvement.created_at < end_datetime,
            )
        )

        # =====================================================
        # TOTAL IMPROVEMENT
        # =====================================================

        total_improvement = (
            period_query
            .count()
        )

        # =====================================================
        # COMPLETED
        # =====================================================

        completed_improvement = (
            period_query
            .filter(
                Improvement.approved_date.isnot(None),
            )
            .count()
        )

        # =====================================================
        # OPEN
        # =====================================================

        open_improvement = (
            period_query
            .filter(
                Improvement.approved_date.is_(None),
                Improvement.verification_result.is_(None),
                Improvement.implementation_result.is_(None),
            )
            .count()
        )

        # =====================================================
        # IMPLEMENTED
        # =====================================================

        implemented_improvement = (
            period_query
            .filter(
                Improvement.approved_date.is_(None),
                Improvement.verification_result.is_(None),
                Improvement.implementation_result.isnot(None),
            )
            .count()
        )

        # =====================================================
        # VERIFIED
        # =====================================================

        verified_improvement = (
            period_query
            .filter(
                Improvement.approved_date.is_(None),
                Improvement.verification_result.isnot(None),
            )
            .count()
        )

        # =====================================================
        # FINANCIAL SUMMARY
        # LAST 6 MONTHS
        # =====================================================

        financial_row = (
            period_query
            .with_entities(
                func.coalesce(
                    func.sum(
                        Improvement.improvement_cost
                    ),
                    0,
                ).label("total_cost"),

                func.coalesce(
                    func.sum(
                        Improvement.estimated_cost_saving
                    ),
                    0,
                ).label("total_saving"),

                func.coalesce(
                    func.sum(
                        Improvement.estimated_benefit
                    ),
                    0,
                ).label("total_benefit"),

                func.coalesce(
                    func.sum(
                        Improvement.estimated_time_saving
                    ),
                    0,
                ).label("total_time_saving"),
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

        total_time_saving = float(
            financial_row.total_time_saving or 0
        )

        # =====================================================
        # NET BENEFIT
        # =====================================================

        net_benefit = (
            total_benefit
            - total_cost
        )

        # =====================================================
        # IMPROVEMENT TREND
        # =====================================================

        trend_rows = (
            period_query
            .with_entities(
                func.year(
                    Improvement.created_at
                ).label("year"),

                func.month(
                    Improvement.created_at
                ).label("month"),

                func.count(
                    Improvement.id
                ).label("total"),
            )
            .group_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                ),
            )
            .order_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                ),
            )
            .all()
        )

        trend_map = {
            (
                row.year,
                row.month,
            ): row.total
            for row in trend_rows
        }

        improvement_trend = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month,
            )

            improvement_trend.append(
                {
                    "year": current_month.year,
                    "month": current_month.month,
                    "label": current_month.strftime(
                        "%b %Y"
                    ),
                    "total": trend_map.get(
                        key,
                        0,
                    ),
                }
            )

            current_month += relativedelta(
                months=1
            )

        # =====================================================
        # COST SAVING TREND
        # =====================================================

        saving_rows = (
            period_query
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
                    0,
                ).label("saving"),
            )
            .group_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                ),
            )
            .order_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                ),
            )
            .all()
        )

        saving_map = {
            (
                row.year,
                row.month,
            ): float(row.saving or 0)
            for row in saving_rows
        }

        saving_trend = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month,
            )

            saving_trend.append(
                {
                    "year": current_month.year,
                    "month": current_month.month,
                    "label": current_month.strftime(
                        "%b %Y"
                    ),
                    "saving": saving_map.get(
                        key,
                        0,
                    ),
                }
            )

            current_month += relativedelta(
                months=1
            )

        # =====================================================
        # IMPROVEMENT COST TREND
        # =====================================================

        cost_rows = (
            period_query
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
                    0,
                ).label("cost"),
            )
            .group_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                ),
            )
            .order_by(
                func.year(
                    Improvement.created_at
                ),
                func.month(
                    Improvement.created_at
                ),
            )
            .all()
        )

        cost_map = {
            (
                row.year,
                row.month,
            ): float(row.cost or 0)
            for row in cost_rows
        }

        cost_trend = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month,
            )

            cost_trend.append(
                {
                    "year": current_month.year,
                    "month": current_month.month,
                    "label": current_month.strftime(
                        "%b %Y"
                    ),
                    "cost": cost_map.get(
                        key,
                        0,
                    ),
                }
            )

            current_month += relativedelta(
                months=1
            )

        # =====================================================
        # IMPROVEMENT BY DEPARTMENT
        # =====================================================

        department_rows = (
            period_query
            .outerjoin(
                Department,
                Problem.department_id == Department.id,
            )
            .with_entities(
                Department.department_name.label(
                    "department_name"
                ),

                func.count(
                    Improvement.id
                ).label("total"),
            )
            .group_by(
                Department.id,
                Department.department_name,
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

            department_data.append(
                {
                    "department": (
                        row.department_name
                        if row.department_name
                        else "-"
                    ),
                    "total": row.total,
                }
            )

        # =====================================================
        # RETURN
        # =====================================================

        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },

            "summary": {
                "total": total_improvement,
                "completed": completed_improvement,
                "open": open_improvement,
                "implemented": implemented_improvement,
                "verified": verified_improvement,

                "total_cost": total_cost,
                "total_saving": total_saving,
                "total_benefit": total_benefit,
                "net_benefit": net_benefit,
                "total_time_saving": total_time_saving,
            },

            "trend": improvement_trend,

            "saving_trend": saving_trend,

            "cost_trend": cost_trend,

            "by_department": department_data,
        }

    # =========================================================
    # IMPROVEMENT DETAIL
    # =========================================================

    def get_improvement_detail(
        self,
        improvement_id,
    ):

        improvement = (
            db.session.query(Improvement)
            .filter(
                Improvement.id == improvement_id,
                Improvement.is_active.is_(True),
            )
            .first()
        )

        return improvement

    # =========================================================
    # BENEFIT
    # =========================================================

    def calculate_benefit(
        self,
        improvement_id,
    ):

        improvement = (
            db.session.query(Improvement)
            .filter(
                Improvement.id == improvement_id,
                Improvement.is_active.is_(True),
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
                "roi": 0,
            }

        cost = float(
            improvement.improvement_cost or 0
        )

        cost_saving = float(
            improvement.estimated_cost_saving or 0
        )

        time_saving = float(
            improvement.estimated_time_saving or 0
        )

        benefit = float(
            improvement.estimated_benefit or 0
        )

        net_benefit = (
            benefit - cost
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
            "roi": roi,
        }