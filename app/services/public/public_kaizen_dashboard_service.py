from datetime import (
    date,
    datetime,
    timedelta,
)

from dateutil.relativedelta import relativedelta

from sqlalchemy import func

from app.extensions import db

from app.models.kaizen import Kaizen
from app.models.department import Department
from app.models.kaizen_reporting_period import (
    KaizenReportingPeriod
)

from app.models.kaizen_department_target import (
    KaizenDepartmentTarget
)

class PublicKaizenDashboardService:

    # =========================================================
    # PERIOD
    # =========================================================

    def get_period(self):

        today = date.today()

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today

        return {
            "start_date": start_date,
            "end_date": end_date,
        }


    # =========================================================
    # DASHBOARD
    # =========================================================

    def get_dashboard(self):

        period = self.get_period()

        start_date = period["start_date"]
        end_date = period["end_date"]

        # -----------------------------------------------------
        # Datetime range
        #
        # created_at is DateTime.
        # Use < next day to include all records today.
        # -----------------------------------------------------

        start_datetime = datetime.combine(
            start_date,
            datetime.min.time(),
        )

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            datetime.min.time(),
        )

        # -----------------------------------------------------
        # Base Query
        # -----------------------------------------------------

        base_query = (
            db.session.query(Kaizen)
            .filter(
                Kaizen.is_active.is_(True)
            )
        )

        # -----------------------------------------------------
        # Period Query
        # -----------------------------------------------------

        period_query = (
            base_query
            .filter(
                Kaizen.created_at >= start_datetime,
                Kaizen.created_at < end_datetime,
            )
        )

        # =====================================================
        # KPI
        # =====================================================

        total_kaizen = (
            period_query.count()
        )

        approved_kaizen = (
            period_query
            .filter(
                Kaizen.approved_at.isnot(None)
            )
            .count()
        )

        rejected_kaizen = (
            period_query
            .filter(
                Kaizen.rejected_at.isnot(None)
            )
            .count()
        )

        # -----------------------------------------------------
        # OPEN
        #
        # All active Kaizen that are not approved
        # and not rejected.
        # -----------------------------------------------------

        open_kaizen = (
            base_query
            .filter(
                Kaizen.approved_at.is_(None),
                Kaizen.rejected_at.is_(None),
            )
            .count()
        )

        # =====================================================
        # COST SAVING
        # =====================================================

        financial = (
            period_query
            .with_entities(
                func.coalesce(
                    func.sum(
                        Kaizen.cost_saving
                    ),
                    0,
                ).label(
                    "cost_saving"
                )
            )
            .first()
        )

        total_cost_saving = (
            float(
                financial.cost_saving or 0
            )
            if financial
            else 0
        )

        # =====================================================
        # STATUS
        # =====================================================

        status_rows = (
            period_query
            .with_entities(
                Kaizen.status.label(
                    "status"
                ),
                func.count(
                    Kaizen.id
                ).label(
                    "total"
                ),
            )
            .group_by(
                Kaizen.status
            )
            .order_by(
                func.count(
                    Kaizen.id
                ).desc()
            )
            .all()
        )

        status_data = [

            {
                "status": (
                    row.status
                    or "-"
                ),

                "total": row.total,
            }

            for row in status_rows

        ]

        # =====================================================
        # AGING
        #
        # Aging only for currently open Kaizen.
        # =====================================================

        aging = {
            "0_7": 0,
            "8_14": 0,
            "15_30": 0,
            "31_60": 0,
            "over_60": 0,
        }

        open_rows = (
            base_query
            .filter(
                Kaizen.approved_at.is_(None),
                Kaizen.rejected_at.is_(None),
            )
            .with_entities(
                Kaizen.created_at
            )
            .all()
        )

        for row in open_rows:

            if not row.created_at:
                continue

            created_date = (
                row.created_at.date()
            )

            aging_days = (
                end_date
                - created_date
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

        # =====================================================
        # MONTHLY TREND
        # =====================================================

        trend = []

        saving_trend = []

        first_month = (
            start_date.replace(day=1)
        )

        for i in range(6):

            month_date = (
                first_month
                + relativedelta(
                    months=i
                )
            )

            next_month = (
                month_date
                + relativedelta(
                    months=1
                )
            )

            month_start = datetime.combine(
                month_date,
                datetime.min.time(),
            )

            month_end = datetime.combine(
                next_month,
                datetime.min.time(),
            )

            # -------------------------------------------------
            # Count
            # -------------------------------------------------

            monthly_query = (
                base_query
                .filter(
                    Kaizen.created_at >= month_start,
                    Kaizen.created_at < month_end,
                )
            )

            total = (
                monthly_query.count()
            )

            trend.append(
                {
                    "month": (
                        month_date.strftime(
                            "%b %Y"
                        )
                    ),
                    "total": total,
                }
            )

            # -------------------------------------------------
            # Cost Saving
            # -------------------------------------------------

            saving = (
                monthly_query
                .with_entities(
                    func.coalesce(
                        func.sum(
                            Kaizen.cost_saving
                        ),
                        0,
                    )
                )
                .scalar()
            )

            saving_trend.append(
                {
                    "month": (
                        month_date.strftime(
                            "%b %Y"
                        )
                    ),
                    "saving": float(
                        saving or 0
                    ),
                }
            )

        # =====================================================
        # DEPARTMENT
        # =====================================================

        department_rows = (
            period_query
            .join(
                Department,
                Kaizen.department_id
                == Department.id,
            )
            .with_entities(
                Department.id.label(
                    "department_id"
                ),
                Department.department_name.label(
                    "department_name"
                ),
                func.count(
                    Kaizen.id
                ).label(
                    "total"
                ),
            )
            .group_by(
                Department.id,
                Department.department_name,
            )
            .order_by(
                func.count(
                    Kaizen.id
                ).desc()
            )
            .all()
        )

        department_data = [

            {
                "department_id":
                    row.department_id,

                "department":
                    row.department_name,

                "total":
                    row.total,
            }

            for row in department_rows

        ]

        # =========================================================
        # CURRENT KAIZEN REPORTING PERIOD
        # =========================================================

        current_reporting_period = (
            db.session.query(
                KaizenReportingPeriod
            )
            .filter(
                KaizenReportingPeriod.is_active.is_(True),

                KaizenReportingPeriod.start_date <= end_date,

                KaizenReportingPeriod.end_date >= end_date,
            )
            .order_by(
                KaizenReportingPeriod.start_date.desc()
            )
            .first()
        )


        # =========================================================
        # TARGET VS RESULT
        # =========================================================

        target_vs_result = []

        if current_reporting_period:

            reporting_start = (
                current_reporting_period.start_date
            )

            reporting_end = (
                current_reporting_period.end_date
            )

            # -----------------------------------------------------
            # Target
            # -----------------------------------------------------

            target_rows = (
                db.session.query(
                    KaizenDepartmentTarget.department_id,

                    Department.department_name,

                    KaizenDepartmentTarget.target_quantity,
                )
                .join(
                    Department,
                    KaizenDepartmentTarget.department_id
                    == Department.id
                )
                .filter(
                    KaizenDepartmentTarget.is_active.is_(True),

                    Department.is_active.is_(True),

                    KaizenDepartmentTarget.reporting_period_id
                    == current_reporting_period.id,
                )
                .order_by(
                    Department.department_name.asc()
                )
                .all()
            )


            # -----------------------------------------------------
            # Actual / Result
            #
            # Semua Kaizen aktif yang dibuat dalam
            # reporting period yang sedang berlangsung.
            # -----------------------------------------------------

            reporting_end_exclusive = (
                reporting_end
                + timedelta(days=1)
            )

            actual_rows = (
                db.session.query(
                    Kaizen.department_id,

                    func.count(
                        Kaizen.id
                    ).label("actual"),
                )
                .filter(
                    Kaizen.is_active.is_(True),

                    Kaizen.created_at >= reporting_start,

                    Kaizen.created_at < reporting_end_exclusive,
                )
                .group_by(
                    Kaizen.department_id
                )
                .all()
            )


            # -----------------------------------------------------
            # Actual Map
            # -----------------------------------------------------

            actual_map = {

                row.department_id:
                    int(row.actual or 0)

                for row in actual_rows

            }


            # -----------------------------------------------------
            # Target Map
            # -----------------------------------------------------

            target_map = {

                row.department_id: {

                    "department":
                        row.department_name,

                    "target":
                        int(
                            row.target_quantity or 0
                        ),

                }

                for row in target_rows

            }


            # -----------------------------------------------------
            # Department IDs
            #
            # Gabungkan department yang memiliki target
            # dan department yang memiliki actual.
            # -----------------------------------------------------

            department_ids = set(
                target_map.keys()
            )

            department_ids.update(
                actual_map.keys()
            )


            # -----------------------------------------------------
            # Get Department Names for actual-only departments
            # -----------------------------------------------------

            actual_only_department_ids = (
                department_ids
                - set(target_map.keys())
            )


            actual_department_names = {}

            if actual_only_department_ids:

                department_rows = (
                    db.session.query(
                        Department.id,
                        Department.department_name,
                    )
                    .filter(
                        Department.id.in_(
                            actual_only_department_ids
                        ),

                        Department.is_active.is_(True),
                    )
                    .all()
                )

                actual_department_names = {

                    row.id:
                        row.department_name

                    for row in department_rows

                }


            # -----------------------------------------------------
            # Build Chart Data
            # -----------------------------------------------------

            for department_id in sorted(
                department_ids
            ):

                if department_id in target_map:

                    department_name = (
                        target_map[
                            department_id
                        ]["department"]
                    )

                    target = (
                        target_map[
                            department_id
                        ]["target"]
                    )

                else:

                    department_name = (
                        actual_department_names.get(
                            department_id,
                            "-"
                        )
                    )

                    target = 0


                actual = (
                    actual_map.get(
                        department_id,
                        0
                    )
                )


                achievement = (

                    (
                        actual / target
                    ) * 100

                    if target > 0

                    else 0

                )


                target_vs_result.append({

                    "department_id":
                        department_id,

                    "department":
                        department_name,

                    "target":
                        target,

                    "actual":
                        actual,

                    "achievement":
                        achievement,

                })


        # =========================================================
        # CURRENT REPORTING PERIOD INFO
        # =========================================================

        current_period_data = None

        if current_reporting_period:

            current_period_data = {

                "id":
                    current_reporting_period.id,

                "period_code":
                    current_reporting_period.period_code,

                "period_name":
                    current_reporting_period.period_name,

                "start_date":
                    current_reporting_period.start_date,

                "end_date":
                    current_reporting_period.end_date,

            }

        # =====================================================
        # RETURN
        # =====================================================

        return {

            "period": period,

            "summary": {

                "total":
                    total_kaizen,

                "approved":
                    approved_kaizen,

                "rejected":
                    rejected_kaizen,

                "open":
                    open_kaizen,

                "cost_saving":
                    total_cost_saving,
            },

            "status":
                status_data,

            "aging":
                aging,

            "trend":
                trend,

            "saving_trend":
                saving_trend,

            "by_department":
                department_data,
        }


    # =========================================================
    # DETAIL
    # =========================================================

    def get_detail(
        self,
        kaizen_id
    ):

        kaizen = (
            db.session.query(
                Kaizen
            )
            .filter(
                Kaizen.id == kaizen_id,

                Kaizen.is_active.is_(True),
            )
            .first()
        )

        return kaizen