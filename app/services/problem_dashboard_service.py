from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, or_

from app.extensions import db
from app.models.problem import Problem
from app.core.choices.problem import ProblemPriority, ProblemStatus


class ProblemDashboardService:

    def get_dashboard(
        self,
        page=1,
        per_page=10,
        search=None,
        status=None,
        priority=None
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
        # OPEN PROBLEM
        # =========================================================

        open_statuses = [
            ProblemStatus.OPEN,
            ProblemStatus.IN_PROGRESS
        ]

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
        # PROBLEM TREND
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
        # PROBLEM LOSS
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
        # AGING
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
        # PROBLEM LIST
        # =========================================================

        query = (
            db.session.query(Problem)
            .filter(
                Problem.is_active.is_(True)
            )
        )

        # SEARCH

        if search:

            keyword = (
                f"%{search.strip()}%"
            )

            query = query.filter(
                or_(
                    Problem.problem_no.ilike(
                        keyword
                    ),

                    Problem.title.ilike(
                        keyword
                    ),

                    Problem.description.ilike(
                        keyword
                    )
                )
            )

        # STATUS

        if status:

            query = query.filter(
                Problem.status == status
            )

        # PRIORITY

        if priority:

            query = query.filter(
                Problem.priority == priority
            )

        # ORDER

        query = query.order_by(
            Problem.problem_date.desc(),
            Problem.id.desc()
        )

        # PAGINATION

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        problems = []

        for problem in pagination.items:

            if problem.problem_date:

                aging_days = (
                    today -
                    problem.problem_date
                ).days

            else:

                aging_days = 0

            # Aging hanya untuk problem
            # yang belum selesai

            if problem.status not in open_statuses:

                aging_days = None

            problems.append({
                "id": problem.id,
                "problem_no": problem.problem_no,
                "problem_date": problem.problem_date,
                "title": problem.title,

                "department": (
                    problem.department.department_name
                    if problem.department
                    else "-"
                ),

                "priority": problem.priority,
                "status": problem.status,

                "aging_days": aging_days,

                "loss_cost": float(
                    problem.loss_cost or 0
                )
            })

        return {

            "period": {
                "start_date": start_date,
                "end_date": end_date
            },

            "summary": {
                "open": open_count,
                "on_progress": on_progress_count,
                "total_open": total_open,
                "total_loss": total_loss
            },

            "trend": problem_trend,

            "loss_trend": problem_loss_trend,

            "aging": aging,

            "problems": problems,

            "pagination": pagination,

            "search": search or "",

            "status": status or "",

            "priority": priority or ""
        }

    def get_problem_detail(self, problem_id):

        problem = (
            db.session.query(Problem)
            .filter(
                Problem.id == problem_id,
                Problem.is_active.is_(True)
            )
            .first()
        )

        return problem