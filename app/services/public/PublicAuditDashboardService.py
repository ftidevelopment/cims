from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from sqlalchemy import func

from app.extensions import db

from app.models.audit import Audit
from app.models.audit_execution import AuditExecution
from app.models.audit_assignment import AuditAssignment
from app.models.audit_finding import AuditFinding
from app.models.department import Department


class PublicAuditDashboardService:
    """
    Public Audit Dashboard Service.

    Dashboard menampilkan KPI Audit secara keseluruhan
    untuk periode 6 bulan terakhir.

    Struktur dashboard:

    period
    summary
    status
    severity
    trend
    by_department

    Periode:
    - Audit       : menggunakan Audit.audit_date
    - Finding     : menggunakan AuditFinding.created_at

    Overdue:
    - target_date < today
    - status != CLOSED
    """

    # =========================================================
    # PERIOD
    # =========================================================

    def get_period(self):
        """
        Get dashboard period.

        Period:
        - Start : first day of current month - 5 months
        - End   : today

        Example:
        October 2026
        -> May 2026 sampai October 2026
        """

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
        """
        Get complete public Audit Dashboard data.
        """

        period = self.get_period()

        start_date = period["start_date"]
        end_date = period["end_date"]

        # -----------------------------------------------------
        # Datetime range
        # -----------------------------------------------------

        start_datetime = datetime.combine(
            start_date,
            datetime.min.time(),
        )

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            datetime.min.time(),
        )

        # =====================================================
        # BASE QUERY
        # =====================================================

        audit_base_query = (
            db.session.query(Audit)
            .filter(
                Audit.is_active.is_(True)
            )
        )

        finding_base_query = (
            db.session.query(AuditFinding)
            .filter(
                AuditFinding.is_active.is_(True)
            )
        )

        # =====================================================
        # PERIOD QUERY - AUDIT
        #
        # Audit menggunakan audit_date
        # =====================================================

        audit_period_query = (
            audit_base_query
            .filter(
                Audit.audit_date >= start_date,
                Audit.audit_date <= end_date,
            )
        )

        # =====================================================
        # PERIOD QUERY - FINDING
        #
        # Finding menggunakan created_at
        # =====================================================

        finding_period_query = (
            finding_base_query
            .filter(
                AuditFinding.created_at >= start_datetime,
                AuditFinding.created_at < end_datetime,
            )
        )

        # =====================================================
        # SUMMARY
        # =====================================================

        # -----------------------------------------------------
        # Total Audit
        # -----------------------------------------------------

        total_audit = (
            audit_period_query.count()
        )

        # -----------------------------------------------------
        # Completed Audit
        # -----------------------------------------------------

        completed_audit = (
            audit_period_query
            .filter(
                Audit.status == "COMPLETED"
            )
            .count()
        )

        # -----------------------------------------------------
        # Total Finding
        # -----------------------------------------------------

        total_findings = (
            finding_period_query.count()
        )

        # -----------------------------------------------------
        # Closed Finding
        #
        # Menggunakan seluruh finding aktif,
        # bukan hanya finding periode.
        #
        # Hal ini berguna untuk menunjukkan kondisi
        # current finding.
        # -----------------------------------------------------

        closed_findings = (
            finding_base_query
            .filter(
                AuditFinding.status == "CLOSED"
            )
            .count()
        )

        # -----------------------------------------------------
        # Open Finding
        # -----------------------------------------------------

        open_findings = (
            finding_base_query
            .filter(
                AuditFinding.status != "CLOSED"
            )
            .count()
        )

        # -----------------------------------------------------
        # Verification Pending
        # -----------------------------------------------------

        verification_pending = (
            finding_base_query
            .filter(
                AuditFinding.status
                == "AUDITOR_VERIFICATION"
            )
            .count()
        )

        # -----------------------------------------------------
        # Overdue Finding
        #
        # Overdue bukan status.
        #
        # Condition:
        # target_date < today
        # AND status != CLOSED
        # -----------------------------------------------------

        overdue_findings = (
            finding_base_query
            .filter(
                AuditFinding.target_date.isnot(None),
                AuditFinding.target_date < end_date,
                AuditFinding.status != "CLOSED",
            )
            .count()
        )

        # =====================================================
        # FINDING STATUS
        # =====================================================

        status_rows = (
            finding_period_query
            .with_entities(
                AuditFinding.status.label(
                    "status"
                ),
                func.count(
                    AuditFinding.id
                ).label(
                    "total"
                ),
            )
            .group_by(
                AuditFinding.status
            )
            .order_by(
                func.count(
                    AuditFinding.id
                ).desc()
            )
            .all()
        )

        status_data = [
            {
                "status": (
                    row.status
                    if row.status
                    else "-"
                ),
                "total": row.total,
            }
            for row in status_rows
        ]

        # =====================================================
        # FINDING SEVERITY
        # =====================================================

        severity_rows = (
            finding_period_query
            .with_entities(
                AuditFinding.severity.label(
                    "severity"
                ),
                func.count(
                    AuditFinding.id
                ).label(
                    "total"
                ),
            )
            .group_by(
                AuditFinding.severity
            )
            .order_by(
                func.count(
                    AuditFinding.id
                ).desc()
            )
            .all()
        )

        severity_data = [
            {
                "severity": (
                    row.severity
                    if row.severity
                    else "-"
                ),
                "total": row.total,
            }
            for row in severity_rows
        ]

        # =====================================================
        # MONTHLY TREND
        # =====================================================

        trend = []

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

            # -------------------------------------------------
            # Audit period
            #
            # Audit menggunakan audit_date
            # -------------------------------------------------

            monthly_audit_query = (
                audit_base_query
                .filter(
                    Audit.audit_date >= month_date,
                    Audit.audit_date < next_month,
                )
            )

            monthly_audit_total = (
                monthly_audit_query.count()
            )

            monthly_audit_completed = (
                monthly_audit_query
                .filter(
                    Audit.status == "COMPLETED"
                )
                .count()
            )

            # -------------------------------------------------
            # Finding period
            #
            # Finding menggunakan created_at
            # -------------------------------------------------

            month_start_datetime = datetime.combine(
                month_date,
                datetime.min.time(),
            )

            month_end_datetime = datetime.combine(
                next_month,
                datetime.min.time(),
            )

            monthly_finding_query = (
                finding_base_query
                .filter(
                    AuditFinding.created_at
                    >= month_start_datetime,

                    AuditFinding.created_at
                    < month_end_datetime,
                )
            )

            monthly_finding_total = (
                monthly_finding_query.count()
            )

            monthly_finding_closed = (
                monthly_finding_query
                .filter(
                    AuditFinding.status == "CLOSED"
                )
                .count()
            )

            trend.append(
                {
                    "month": (
                        month_date.strftime(
                            "%b %Y"
                        )
                    ),

                    "audit":
                        monthly_audit_total,

                    "audit_completed":
                        monthly_audit_completed,

                    "findings":
                        monthly_finding_total,

                    "findings_closed":
                        monthly_finding_closed,
                }
            )

        # =====================================================
        # BY DEPARTMENT
        #
        # Relationship:
        #
        # AuditFinding
        #     ↓
        # AuditExecution
        #     ↓
        # AuditAssignment
        #     ↓
        # Department
        #
        # Department berada di AuditAssignment.
        # =====================================================

        department_rows = (
            finding_period_query

            .join(
                AuditExecution,
                AuditFinding.audit_execution_id
                == AuditExecution.id,
            )

            .join(
                AuditAssignment,
                AuditExecution.audit_assignment_id
                == AuditAssignment.id,
            )

            .join(
                Department,
                AuditAssignment.department_id
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
                    AuditFinding.id
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
                    AuditFinding.id
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

        # =====================================================
        # RETURN DASHBOARD
        # =====================================================

        return {

            # -------------------------------------------------
            # Period
            # -------------------------------------------------

            "period": period,

            # -------------------------------------------------
            # Summary
            # -------------------------------------------------

            "summary": {

                "total_audit":
                    total_audit,

                "completed_audit":
                    completed_audit,

                "total_findings":
                    total_findings,

                "open_findings":
                    open_findings,

                "overdue_findings":
                    overdue_findings,

                "verification_pending":
                    verification_pending,

                "closed_findings":
                    closed_findings,
            },

            # -------------------------------------------------
            # Finding Status
            # -------------------------------------------------

            "status":
                status_data,

            # -------------------------------------------------
            # Finding Severity
            # -------------------------------------------------

            "severity":
                severity_data,

            # -------------------------------------------------
            # Monthly Trend
            # -------------------------------------------------

            "trend":
                trend,

            # -------------------------------------------------
            # Finding by Department
            # -------------------------------------------------

            "by_department":
                department_data,
        }