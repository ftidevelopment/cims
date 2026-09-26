from datetime import date, datetime, time, timedelta

from sqlalchemy import func

from app.extensions import db
from app.models.kaizen import Kaizen
from app.models.kaizen_reporting_period import KaizenReportingPeriod
from app.models.kaizen_department_target import KaizenDepartmentTarget
from app.models.department import Department


class KaizenTargetResultService:

    def get_reporting_periods(self):
        """
        Get all active Kaizen Reporting Periods.
        """

        return (
            db.session.query(KaizenReportingPeriod)
            .filter(
                KaizenReportingPeriod.is_active.is_(True)
            )
            .order_by(
                KaizenReportingPeriod.start_date.desc(),
                KaizenReportingPeriod.id.desc(),
            )
            .all()
        )

    def get_current_reporting_period(self):
        """
        Get the active Reporting Period based on today's date.
        """

        today = date.today()

        return (
            db.session.query(KaizenReportingPeriod)
            .filter(
                KaizenReportingPeriod.start_date <= today,
                KaizenReportingPeriod.end_date >= today,
                KaizenReportingPeriod.is_active.is_(True),
            )
            .order_by(
                KaizenReportingPeriod.start_date.desc()
            )
            .first()
        )

    def get_reporting_period(self, period_id=None):
        """
        Get selected Reporting Period.

        If period_id is provided:
            return that period.

        If period_id is not provided:
            return current active Reporting Period.
        """

        if period_id:
            try:
                period_id = int(period_id)
            except (TypeError, ValueError):
                period_id = None

        if period_id:
            period = (
                db.session.query(KaizenReportingPeriod)
                .filter(
                    KaizenReportingPeriod.id == period_id,
                    KaizenReportingPeriod.is_active.is_(True),
                )
                .first()
            )

            if period:
                return period

        return self.get_current_reporting_period()

    def get_target_by_department(self, reporting_period_id):
        """
        Get Kaizen target by department
        for the selected Reporting Period.
        """

        rows = (
            db.session.query(
                KaizenDepartmentTarget.department_id,
                Department.department_name,
                KaizenDepartmentTarget.target_quantity,
            )
            .join(
                Department,
                KaizenDepartmentTarget.department_id == Department.id,
            )
            .filter(
                KaizenDepartmentTarget.reporting_period_id
                == reporting_period_id,
                KaizenDepartmentTarget.is_active.is_(True),
                Department.is_active.is_(True),
            )
            .order_by(
                Department.department_name.asc()
            )
            .all()
        )

        return rows

    def get_result_by_department(
        self,
        reporting_start,
        reporting_end,
    ):
        """
        Count Kaizen Result by Department
        based on Kaizen.created_at.
        """

        reporting_start_datetime = datetime.combine(
            reporting_start,
            time.min,
        )

        reporting_end_datetime = datetime.combine(
            reporting_end + timedelta(days=1),
            time.min,
        )

        rows = (
            db.session.query(
                Kaizen.department_id,
                func.count(Kaizen.id).label("result"),
            )
            .filter(
                Kaizen.is_active.is_(True),
                Kaizen.created_at >= reporting_start_datetime,
                Kaizen.created_at < reporting_end_datetime,
            )
            .group_by(
                Kaizen.department_id
            )
            .all()
        )

        return rows

    def get_target_result(self, period_id=None):
        """
        Get complete Kaizen Target vs Result data
        for the selected Reporting Period.
        """

        reporting_period = self.get_reporting_period(
            period_id=period_id
        )

        periods = self.get_reporting_periods()

        if not reporting_period:
            return {
                "period": None,
                "periods": periods,
                "summary": {
                    "total_target": 0,
                    "total_result": 0,
                    "achievement": 0,
                    "department_count": 0,
                },
                "departments": [],
            }

        target_rows = self.get_target_by_department(
            reporting_period_id=reporting_period.id
        )

        result_rows = self.get_result_by_department(
            reporting_start=reporting_period.start_date,
            reporting_end=reporting_period.end_date,
        )

        result_map = {
            row.department_id: int(row.result or 0)
            for row in result_rows
        }

        departments = []

        for row in target_rows:

            target = int(row.target_quantity or 0)

            result = result_map.get(
                row.department_id,
                0,
            )

            if target > 0:
                achievement = round(
                    (result / target) * 100,
                    1,
                )
            else:
                achievement = 0

            gap = result - target

            departments.append({
                "department_id": row.department_id,
                "department_name": row.department_name,
                "target": target,
                "result": result,
                "achievement": achievement,
                "gap": gap,
            })

        total_target = sum(
            item["target"]
            for item in departments
        )

        total_result = sum(
            item["result"]
            for item in departments
        )

        if total_target > 0:
            total_achievement = round(
                (total_result / total_target) * 100,
                1,
            )
        else:
            total_achievement = 0

        return {
            "period": {
                "id": reporting_period.id,
                "code": reporting_period.period_code,
                "name": reporting_period.period_name,
                "start_date": reporting_period.start_date,
                "end_date": reporting_period.end_date,
            },

            "periods": periods,

            "summary": {
                "total_target": total_target,
                "total_result": total_result,
                "achievement": total_achievement,
                "department_count": len(departments),
            },

            "departments": departments,
        }