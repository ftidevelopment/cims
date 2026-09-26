from datetime import date, datetime, timedelta

from sqlalchemy import func, or_

from app.extensions import db
from app.models.kaizen import Kaizen
from app.models.department import Department
from app.models.kaizen_department_target import KaizenDepartmentTarget
from app.models.kaizen_reporting_period import KaizenReportingPeriod


class KaizenDashboardService:

    # =========================================================
    # PUBLIC DASHBOARD
    # =========================================================

    def get_dashboard(
        self,
        page=1,
        per_page=10,
        search="",
        status="",
        department_id=""
    ):

        today = date.today()

        trend_period_start = self._subtract_months(today, 5).replace(day=1)
        trend_period_end = today
        # -----------------------------------------------------
        # ACTIVE REPORTING PERIOD
        # -----------------------------------------------------

        current_period = (
            db.session.query(KaizenReportingPeriod)
            .filter(
                KaizenReportingPeriod.start_date <= today,
                KaizenReportingPeriod.end_date >= today,
                KaizenReportingPeriod.is_active.is_(True)
            )
            .order_by(
                KaizenReportingPeriod.start_date.desc()
            )
            .first()
        )

        # -----------------------------------------------------
        # Base Query
        # -----------------------------------------------------

        base_query = (
            db.session.query(Kaizen)
            .join(
                Department,
                Kaizen.department_id == Department.id
            )
            .filter(
                Kaizen.is_active.is_(True)
            )
        )

        # -----------------------------------------------------
        # SUMMARY
        # -----------------------------------------------------

        total_kaizen = base_query.count()

        approved_kaizen = (
            base_query
            .filter(
                Kaizen.approved_at.isnot(None)
            )
            .count()
        )

        rejected_kaizen = (
            base_query
            .filter(
                Kaizen.rejected_at.isnot(None)
            )
            .count()
        )

        open_kaizen = (
            base_query
            .filter(
                Kaizen.approved_at.is_(None),
                Kaizen.rejected_at.is_(None)
            )
            .count()
        )

        # -----------------------------------------------------
        # FINANCIAL SUMMARY
        # -----------------------------------------------------

        financial = (
            base_query
            .with_entities(
                func.coalesce(
                    func.sum(Kaizen.cost_saving),
                    0
                ).label("cost_saving")
            )
            .first()
        )

        total_cost_saving = (
            financial.cost_saving
            if financial
            else 0
        )

        # -----------------------------------------------------
        # STATUS SUMMARY
        # -----------------------------------------------------

        status_rows = (
            base_query
            .with_entities(
                Kaizen.status.label("status"),
                func.count(Kaizen.id).label("total")
            )
            .group_by(
                Kaizen.status
            )
            .order_by(
                func.count(Kaizen.id).desc()
            )
            .all()
        )

        status_data = [
            {
                "status": row.status or "-",
                "total": row.total
            }
            for row in status_rows
        ]

        # -----------------------------------------------------
        # AGING
        #
        # Aging calculated from created_at
        # -----------------------------------------------------

        aging = {
            "0_7": 0,
            "8_14": 0,
            "15_30": 0,
            "31_60": 0,
            "over_60": 0
        }

        kaizen_dates = (
            base_query
            .with_entities(
                Kaizen.created_at
            )
            .filter(
                Kaizen.approved_at.is_(None),
                Kaizen.rejected_at.is_(None)
            )
            .all()
        )

        for row in kaizen_dates:

            if not row.created_at:
                continue

            created_date = row.created_at.date()

            aging_days = (
                today - created_date
            ).days

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

       # -----------------------------------------------------
        # TREND - LAST 6 MONTHS
        # -----------------------------------------------------

        trend = []

        first_month = (
            today.replace(day=1)
        )

        # -----------------------------------------------------
        # DASHBOARD PERIOD
        # -----------------------------------------------------

        period_start = self._subtract_months(
            first_month,
            5
        )

        period_end = today

        for i in range(5, -1, -1):

            month_date = self._subtract_months(
                first_month,
                i
            )

            next_month = self._add_months(
                month_date,
                1
            )

            start_datetime = datetime.combine(
                month_date,
                datetime.min.time()
            )

            end_datetime = datetime.combine(
                next_month,
                datetime.min.time()
            )

            total = (
                base_query
                .filter(
                    Kaizen.created_at >= start_datetime,
                    Kaizen.created_at < end_datetime
                )
                .count()
            )

            trend.append(
                {
                    "month": month_date.strftime("%b %Y"),
                    "total": total
                }
            )

        # -----------------------------------------------------
        # SAVING TREND
        # -----------------------------------------------------

        saving_trend = []

        for i in range(5, -1, -1):

            month_date = self._subtract_months(
                first_month,
                i
            )

            next_month = self._add_months(
                month_date,
                1
            )

            start_datetime = datetime.combine(
                month_date,
                datetime.min.time()
            )

            end_datetime = datetime.combine(
                next_month,
                datetime.min.time()
            )

            saving = (
                base_query
                .filter(
                    Kaizen.created_at >= start_datetime,
                    Kaizen.created_at < end_datetime
                )
                .with_entities(
                    func.coalesce(
                        func.sum(
                            Kaizen.cost_saving
                        ),
                        0
                    )
                )
                .scalar()
            )

            saving_trend.append(
                {
                    "month": month_date.strftime("%b %Y"),
                    "saving": saving or 0
                }
            )


        # -----------------------------------------------------
        # DEPARTMENT TARGET vs ACTUAL
        # -----------------------------------------------------

        department_data = []

        if current_period:

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

            for department in departments:

                # ---------------------------------------------
                # TARGET
                # ---------------------------------------------

                target_row = (
                    db.session.query(
                        KaizenDepartmentTarget.target_quantity
                    )
                    .filter(
                        KaizenDepartmentTarget.reporting_period_id
                        == current_period.id,

                        KaizenDepartmentTarget.department_id
                        == department.id,

                        KaizenDepartmentTarget.is_active.is_(True)
                    )
                    .first()
                )

                target = (
                    target_row.target_quantity
                    if target_row
                    else 0
                )

                # ---------------------------------------------
                # ACTUAL
                # ---------------------------------------------

                actual = (
                    db.session.query(
                        func.count(Kaizen.id)
                    )
                    .filter(
                        Kaizen.department_id == department.id,

                        Kaizen.is_active.is_(True),

                        # HANYA KAIZEN YANG SUDAH APPROVED
                        Kaizen.approved_at.isnot(None),

                        # SESUAI REPORTING PERIOD
                        Kaizen.created_at >= datetime.combine(
                            current_period.start_date,
                            datetime.min.time()
                        ),

                        Kaizen.created_at < datetime.combine(
                            current_period.end_date + timedelta(days=1),
                            datetime.min.time()
                        )
                    )
                    .scalar()
                    or 0
                )
                # ---------------------------------------------
                # ACHIEVEMENT
                # ---------------------------------------------

                if target > 0:

                    achievement = (
                        actual / target
                    ) * 100

                else:

                    achievement = 0

                department_data.append(
                    {
                        "department_id":
                            department.id,

                        "department":
                            department.department_name,

                        "target":
                            target,

                        "actual":
                            actual,

                        "achievement":
                            achievement
                    }
                )

        # -----------------------------------------------------
        # DEPARTMENT FILTER
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # LIST QUERY
        # -----------------------------------------------------

        list_query = base_query

        # -----------------------------------------------------
        # SEARCH
        # -----------------------------------------------------

        if search:

            keyword = f"%{search.strip()}%"

            list_query = list_query.filter(
                or_(
                    Kaizen.kaizen_no.ilike(
                        keyword
                    ),

                    Kaizen.title.ilike(
                        keyword
                    ),

                    Kaizen.description.ilike(
                        keyword
                    )
                )
            )

        # -----------------------------------------------------
        # STATUS FILTER
        # -----------------------------------------------------

        if status:

            list_query = list_query.filter(
                Kaizen.status == status
            )

        # -----------------------------------------------------
        # DEPARTMENT FILTER
        # -----------------------------------------------------

        if department_id:

            try:

                department_id_int = int(
                    department_id
                )

                list_query = list_query.filter(
                    Kaizen.department_id
                    == department_id_int
                )

            except (TypeError, ValueError):

                pass

        # -----------------------------------------------------
        # PAGINATION
        # -----------------------------------------------------

        pagination = (
            list_query
            .order_by(
                Kaizen.created_at.desc()
            )
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        )

        # -----------------------------------------------------
        # KAIZEN LIST
        # -----------------------------------------------------

        kaizen_list = []

        for item in pagination.items:

            kaizen_list.append(
                {
                    "id": item.id,

                    "kaizen_no":
                        item.kaizen_no,

                    "title":
                        item.title,

                    "department":
                        (
                            item.department.department_name
                            if item.department
                            else "-"
                        ),

                    "status":
                        item.status or "-",

                    "created_at":
                        item.created_at,

                    "implementation_date":
                        item.implementation_date,

                    "cost_saving":
                        item.cost_saving or 0,

                    "approved_at":
                        item.approved_at,

                    "rejected_at":
                        item.rejected_at
                }
            )

        # -----------------------------------------------------
        # RESULT
        # -----------------------------------------------------

       

        return {
            "period": {
                "id": current_period.id if current_period else None,
                "code": current_period.period_code if current_period else None,
                "name": current_period.period_name if current_period else None,
                "start_date": current_period.start_date if current_period else None,
                "end_date": current_period.end_date if current_period else None
            },

           "trend_period": {
                "start_date": trend_period_start,
                "end_date": trend_period_end
            },


            "summary": {

                "total": total_kaizen,

                "approved": approved_kaizen,

                "rejected": rejected_kaizen,

                "open": open_kaizen,

                "cost_saving":
                    total_cost_saving
            },

            "status": status_data,

            "aging": aging,

            "trend": trend,

            "saving_trend": saving_trend,

            "by_department":
                department_data,

            "departments":
                departments,

            "kaizens":
                kaizen_list,

            "pagination":
                pagination,

            "search":
                search,

            "status_filter":
                status,

            "department_filter":
                department_id
        }


    # =========================================================
    # DETAIL
    # =========================================================

    def get_detail(self, kaizen_id):

        kaizen = (
            db.session.query(Kaizen)
            .filter(
                Kaizen.id == kaizen_id,
                Kaizen.is_active.is_(True)
            )
            .first()
        )

        return kaizen


    # =========================================================
    # MONTH HELPER
    # =========================================================

    @staticmethod
    def _subtract_months(
        source_date,
        months
    ):

        year = (
            source_date.year
            - (
                months // 12
            )
        )

        month = (
            source_date.month
            - (
                months % 12
            )
        )

        if month <= 0:

            year -= 1

            month += 12

        return source_date.replace(
            year=year,
            month=month,
            day=1
        )


    @staticmethod
    def _add_months(
        source_date,
        months
    ):

        month = (
            source_date.month
            + months
        )

        year = source_date.year

        while month > 12:

            month -= 12

            year += 1

        while month <= 0:

            month += 12

            year -= 1

        return source_date.replace(
            year=year,
            month=month,
            day=1
        )