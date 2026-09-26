from datetime import date
from dateutil.relativedelta import relativedelta
from app.models.kaizen import Kaizen
from sqlalchemy import func
from app.models.department import Department
from app.extensions import db
from app.models.problem import Problem
from app.models.improvement import Improvement
from app.core.choices.problem import (
    ProblemPriority,
    ProblemStatus,
)


class DashboardService:

    # ==================================================
    # Dashboard 1
    # Problem & Improvement Performance
    # ==================================================

    def get_problem_improvement_dashboard(self):

        today = date.today()

        # --------------------------------------------------
        # Period: Last 6 Months
        # --------------------------------------------------

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today

        # --------------------------------------------------
        # Open Problem by Priority
        # Open = Open + On Progress
        # --------------------------------------------------

        open_statuses = [
            ProblemStatus.OPEN,
            ProblemStatus.IN_PROGRESS,
        ]

        priority_rows = (
            db.session.query(
                Problem.priority,
                func.count(Problem.id)
            )
            .filter(
                Problem.is_active.is_(True),
                Problem.status.in_(open_statuses)
            )
            .group_by(
                Problem.priority
            )
            .all()
        )

        priority_map = {
            priority: count
            for priority, count in priority_rows
        }

        open_problem_high = priority_map.get(
            ProblemPriority.HIGH,
            0
        )

        open_problem_medium = priority_map.get(
            ProblemPriority.MEDIUM,
            0
        )

        open_problem_low = priority_map.get(
            ProblemPriority.LOW,
            0
        )

        # --------------------------------------------------
        # Problem Trend - Last 6 Months
        # --------------------------------------------------

        problem_trend_rows = (
            db.session.query(
                func.year(Problem.problem_date).label("year"),
                func.month(Problem.problem_date).label("month"),
                func.count(Problem.id).label("total")
            )
            .filter(
                Problem.is_active.is_(True),
                Problem.problem_date >= start_date,
                Problem.problem_date <= end_date
            )
            .group_by(
                func.year(Problem.problem_date),
                func.month(Problem.problem_date)
            )
            .order_by(
                func.year(Problem.problem_date),
                func.month(Problem.problem_date)
            )
            .all()
        )

        problem_trend_map = {
            (row.year, row.month): row.total
            for row in problem_trend_rows
        }

        problem_trend = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month
            )

            problem_trend.append({
                "year": current_month.year,
                "month": current_month.month,
                "label": current_month.strftime("%b %Y"),
                "total": problem_trend_map.get(key, 0),
            })

            current_month += relativedelta(months=1)

        # --------------------------------------------------
        # Problem Loss Trend - Last 6 Months
        # --------------------------------------------------

        problem_loss_rows = (
            db.session.query(
                func.year(Problem.problem_date).label("year"),
                func.month(Problem.problem_date).label("month"),
                func.coalesce(
                    func.sum(Problem.loss_cost),
                    0
                ).label("loss")
            )
            .filter(
                Problem.is_active.is_(True),
                Problem.problem_date >= start_date,
                Problem.problem_date <= end_date
            )
            .group_by(
                func.year(Problem.problem_date),
                func.month(Problem.problem_date)
            )
            .order_by(
                func.year(Problem.problem_date),
                func.month(Problem.problem_date)
            )
            .all()
        )

        problem_loss_map = {
            (row.year, row.month): float(row.loss or 0)
            for row in problem_loss_rows
        }

        problem_loss_trend = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month
            )

            problem_loss_trend.append({
                "year": current_month.year,
                "month": current_month.month,
                "label": current_month.strftime("%b %Y"),
                "loss": problem_loss_map.get(key, 0),
            })

            current_month += relativedelta(months=1)

        # --------------------------------------------------
        # Improvement Activity - Last 6 Months
        # Based on approved_date
        # --------------------------------------------------

        improvement_activity_rows = (
            db.session.query(
                func.year(Improvement.approved_date).label("year"),
                func.month(Improvement.approved_date).label("month"),
                func.count(Improvement.id).label("total")
            )
            .filter(
                Improvement.is_active.is_(True),
                Improvement.approved_date.isnot(None),
                Improvement.approved_date >= start_date,
                Improvement.approved_date <= end_date
            )
            .group_by(
                func.year(Improvement.approved_date),
                func.month(Improvement.approved_date)
            )
            .order_by(
                func.year(Improvement.approved_date),
                func.month(Improvement.approved_date)
            )
            .all()
        )

        improvement_activity_map = {
            (row.year, row.month): row.total
            for row in improvement_activity_rows
        }

        improvement_activity = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month
            )

            improvement_activity.append({
                "year": current_month.year,
                "month": current_month.month,
                "label": current_month.strftime("%b %Y"),
                "total": improvement_activity_map.get(
                    key,
                    0
                ),
            })

            current_month += relativedelta(months=1)

        # --------------------------------------------------
        # Improvement Cost - Last 6 Months
        # --------------------------------------------------

        improvement_cost = (
            db.session.query(
                func.coalesce(
                    func.sum(Improvement.improvement_cost),
                    0
                )
            )
            .filter(
                Improvement.is_active.is_(True),
                Improvement.approved_date.isnot(None),
                Improvement.approved_date >= start_date,
                Improvement.approved_date <= end_date
            )
            .scalar()
            or 0
        )

        # --------------------------------------------------
        # Estimated Cost Saving - Last 6 Months
        # --------------------------------------------------

        estimated_cost_saving = (
            db.session.query(
                func.coalesce(
                    func.sum(
                        Improvement.estimated_cost_saving
                    ),
                    0
                )
            )
            .filter(
                Improvement.is_active.is_(True),
                Improvement.approved_date.isnot(None),
                Improvement.approved_date >= start_date,
                Improvement.approved_date <= end_date
            )
            .scalar()
            or 0
        )

        # --------------------------------------------------
        # Net Benefit
        # --------------------------------------------------

        net_benefit = (
            float(estimated_cost_saving or 0)
            - float(improvement_cost or 0)
        )

        # =====================================================
        # KAIZEN TREND - LAST 6 MONTHS
        # =====================================================

        kaizen_trend_rows = (
            db.session.query(
                func.year(Kaizen.implementation_date).label("year"),
                func.month(Kaizen.implementation_date).label("month"),
                func.count(Kaizen.id).label("total")
            )
            .filter(
                Kaizen.is_active.is_(True),
                Kaizen.implementation_date.isnot(None),
                Kaizen.implementation_date >= start_date,
                Kaizen.implementation_date <= end_date
            )
            .group_by(
                func.year(Kaizen.implementation_date),
                func.month(Kaizen.implementation_date)
            )
            .order_by(
                func.year(Kaizen.implementation_date),
                func.month(Kaizen.implementation_date)
            )
            .all()
        )

        kaizen_trend_map = {
            (row.year, row.month): row.total
            for row in kaizen_trend_rows
        }

        kaizen_trend = []

        current_month = start_date

        while current_month <= end_date.replace(day=1):

            key = (
                current_month.year,
                current_month.month
            )

            kaizen_trend.append({
                "year": current_month.year,
                "month": current_month.month,
                "label": current_month.strftime("%b %Y"),
                "total": kaizen_trend_map.get(key, 0)
            })

            current_month += relativedelta(months=1)


        # =====================================================
        # KAIZEN BY DEPARTMENT
        # =====================================================

        kaizen_department_rows = (
            db.session.query(
                Department.department_name.label("department"),
                func.count(Kaizen.id).label("total")
            )
            .join(
                Department,
                Department.id == Kaizen.department_id
            )
            .filter(
                Kaizen.is_active.is_(True),
                Kaizen.implementation_date.isnot(None),
                Kaizen.implementation_date >= start_date,
                Kaizen.implementation_date <= end_date
            )
            .group_by(Department.id, Department.department_name)
            .order_by(func.count(Kaizen.id).desc())
            .all()
        )

        kaizen_by_department = [
            {
                "department": row.department,
                "total": row.total
            }
            for row in kaizen_department_rows
        ]


        # =====================================================
        # TOTAL KAIZEN
        # =====================================================

        total_kaizen = (
            db.session.query(
                func.count(Kaizen.id)
            )
            .filter(
                Kaizen.is_active.is_(True),
                Kaizen.implementation_date.isnot(None),
                Kaizen.implementation_date >= start_date,
                Kaizen.implementation_date <= end_date
            )
            .scalar()
            or 0
        )

        # --------------------------------------------------
        # Return Dashboard Data
        # --------------------------------------------------

        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },

            "open_problem": {
                "high": open_problem_high,
                "medium": open_problem_medium,
                "low": open_problem_low,
                "total": (
                    open_problem_high
                    + open_problem_medium
                    + open_problem_low
                )
            },

            "problem_trend": problem_trend,

            "problem_loss_trend": problem_loss_trend,

            "improvement_activity": improvement_activity,

            "improvement_cost": float(improvement_cost or 0),

            "estimated_cost_saving": float(
                estimated_cost_saving or 0
            ),

            "net_benefit": net_benefit,

            "kaizen": {
                "total": total_kaizen,
                "trend": kaizen_trend,
                "by_department": kaizen_by_department
            }
        }