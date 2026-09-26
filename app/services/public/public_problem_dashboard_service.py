from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy import func

from app.extensions import db
from app.models.problem import Problem
from app.core.choices.problem import ProblemStatus


class PublicProblemDashboardService:

    def get_dashboard(self):

        today = date.today()

        # =========================================================
        # LAST 6 MONTHS
        #
        # Example:
        # If today is September 20, 2026
        # Period = April 1, 2026 - September 20, 2026
        # =========================================================

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today

        # =========================================================
        # STATUS
        #
        # Open / In Progress are NOT limited to 6 months.
        # They represent all active outstanding problems.
        # =========================================================

        open_statuses = [
            ProblemStatus.OPEN,
            ProblemStatus.IN_PROGRESS
        ]

        # =========================================================
        # TOTAL PROBLEM - LAST 6 MONTHS
        # =========================================================

        total_problem = (
            db.session.query(
                func.count(Problem.id)
            )
            .filter(
                Problem.is_active.is_(True),
                Problem.problem_date >= start_date,
                Problem.problem_date <= end_date
            )
            .scalar()
            or 0
        )

        # =========================================================
        # OPEN / IN PROGRESS - ALL ACTIVE DATA
        # =========================================================

        status_rows = (
            db.session.query(
                Problem.status,
                func.count(Problem.id).label("total")
            )
            .filter(
                Problem.is_active.is_(True),
                Problem.status.in_(open_statuses)
            )
            .group_by(
                Problem.status
            )
            .all()
        )

        status_map = {
            row.status: row.total
            for row in status_rows
        }

        open_count = status_map.get(
            ProblemStatus.OPEN,
            0
        )

        on_progress_count = status_map.get(
            ProblemStatus.IN_PROGRESS,
            0
        )

        total_open = (
            open_count +
            on_progress_count
        )

        # =========================================================
        # PROBLEM TREND - LAST 6 MONTHS
        # =========================================================

        trend_rows = (
            db.session.query(
                func.year(
                    Problem.problem_date
                ).label("year"),

                func.month(
                    Problem.problem_date
                ).label("month"),

                func.count(
                    Problem.id
                ).label("total")
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

        trend_map = {
            (row.year, row.month): row.total
            for row in trend_rows
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
                "total": trend_map.get(key, 0)
            })

            current_month += relativedelta(
                months=1
            )

        # =========================================================
        # PROBLEM LOSS - LAST 6 MONTHS
        # =========================================================

        loss_rows = (
            db.session.query(
                func.year(
                    Problem.problem_date
                ).label("year"),

                func.month(
                    Problem.problem_date
                ).label("month"),

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

        loss_map = {
            (row.year, row.month): float(
                row.loss or 0
            )
            for row in loss_rows
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
                "loss": loss_map.get(key, 0)
            })

            current_month += relativedelta(
                months=1
            )

        total_loss = sum(
            item["loss"]
            for item in problem_loss_trend
        )

        # =========================================================
        # AGING - ALL ACTIVE OPEN / IN PROGRESS
        #
        # IMPORTANT:
        # Aging is NOT limited to 6 months.
        # =========================================================

        aging_rows = (
            db.session.query(Problem)
            .filter(
                Problem.is_active.is_(True),
                Problem.status.in_(open_statuses)
            )
            .order_by(
                Problem.problem_date.asc()
            )
            .all()
        )

        aging = {
            "0_7": 0,
            "8_14": 0,
            "15_30": 0,
            "31_60": 0,
            "over_60": 0
        }

        for problem in aging_rows:

            if problem.problem_date:

                aging_days = (
                    today -
                    problem.problem_date
                ).days

            else:

                aging_days = 0

            if aging_days <= 7:

                aging["0_7"] += 1

            elif aging_days <= 14:

                aging["8_14"] += 1

            elif aging_days <= 30:

                aging["15_30"] += 1

            elif aging_days <= 60:

                aging["31_60"] += 1

            else:

                aging["over_60"] += 1

        # =========================================================
        # RETURN DASHBOARD DATA
        # =========================================================

        return {

            "period": {
                "start_date": start_date,
                "end_date": end_date
            },

            "summary": {

                # Total Problem = LAST 6 MONTHS
                "total_problem": total_problem,

                # Open = ALL ACTIVE
                "open": open_count,

                # In Progress = ALL ACTIVE
                "on_progress": on_progress_count,

                # Total Open = ALL ACTIVE
                "total_open": total_open,

                # Problem Loss = LAST 6 MONTHS
                "total_loss": total_loss
            },

            "trend": problem_trend,

            "loss_trend": problem_loss_trend,

            "aging": aging
        }