from datetime import date
from dateutil.relativedelta import relativedelta

from sqlalchemy import or_

from app.extensions import db

from app.models.audit_finding import AuditFinding
from app.models.audit_execution import AuditExecution
from app.models.audit_assignment import AuditAssignment
from app.models.audit import Audit
from app.models.department import Department
from app.models.employee import Employee


class PublicAuditFindingListService:
    """
    Public Audit Finding List Service.

    Menyediakan data Audit Finding untuk public dashboard/list.

    Features:
    - Pagination
    - Search
    - Status filter
    - Severity filter
    - Finding Source filter
    - Department filter
    - PIC filter
    - Overdue filter
    - Period filter
    """

    # =========================================================
    # CONSTANTS
    # =========================================================

    STATUS_OPEN = "OPEN"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_ACTION_COMPLETED = "ACTION_COMPLETED"
    STATUS_AUDITOR_VERIFICATION = "AUDITOR_VERIFICATION"
    STATUS_PASS = "PASS"
    STATUS_CLOSED = "CLOSED"

    SEVERITY_CRITICAL = "CRITICAL"
    SEVERITY_MAJOR = "MAJOR"
    SEVERITY_MINOR = "MINOR"
    SEVERITY_OBSERVATION = "OBSERVATION"

    SOURCE_CHECKLIST = "CHECKLIST"
    SOURCE_OUTSIDE_CHECKLIST = "OUTSIDE_CHECKLIST"

    # =========================================================
    # PERIOD
    # =========================================================

    def get_period(self):
        """
        Get default period.

        Default:
        6 bulan terakhir termasuk bulan berjalan.
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
    # FORMAT DATE
    # =========================================================

    def _format_date(self, value):
        """
        Format date untuk display.
        """

        if not value:
            return "-"

        return value.strftime("%d-%m-%Y")

    # =========================================================
    # GET FINDINGS
    # =========================================================

    def get_findings(
        self,
        page=1,
        per_page=10,
        search="",
        status="",
        severity="",
        finding_source="",
        department_id="",
        pic_employee_id="",
        overdue="",
        period="",
        open_only="",
    ):
        """
        Get paginated public Audit Finding list.

        Features:
        - Pagination
        - Search
        - Status filter
        - Severity filter
        - Finding Source filter
        - Department filter
        - PIC filter
        - Overdue filter
        - Open Finding filter
        - Period filter

        Definitions:

        Total Findings
            = all active findings within selected period.

        Open Findings
            = all active findings with status != CLOSED.

        Overdue
            = target_date < today
            AND status != CLOSED.

        Period
            = based on Audit.audit_date.
        """

        # =====================================================
        # NORMALIZE PAGE
        # =====================================================

        try:
            page = int(page)

        except (TypeError, ValueError):
            page = 1

        if page < 1:
            page = 1


        # =====================================================
        # NORMALIZE PER PAGE
        # =====================================================

        try:
            per_page = int(per_page)

        except (TypeError, ValueError):
            per_page = 10

        if per_page not in [10, 20, 50, 100]:
            per_page = 10


        # =====================================================
        # NORMALIZE FILTER
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

        severity = (
            severity.strip()
            if severity
            else ""
        )

        finding_source = (
            finding_source.strip()
            if finding_source
            else ""
        )

        department_id = (
            str(department_id).strip()
            if department_id
            else ""
        )

        pic_employee_id = (
            str(pic_employee_id).strip()
            if pic_employee_id
            else ""
        )

        overdue = (
            str(overdue).strip()
            if overdue
            else ""
        )

        open_only = (
            str(open_only).strip()
            if open_only
            else ""
        )

        period = (
            period.strip()
            if period
            else ""
        )


        # =====================================================
        # PERIOD
        # =====================================================

        default_period = self.get_period()

        start_date = default_period["start_date"]
        end_date = default_period["end_date"]


        # -----------------------------------------------------
        # period = all
        #
        # No date restriction
        # -----------------------------------------------------

        if period.lower() == "all":

            start_date = None
            end_date = None


        # =====================================================
        # BASE QUERY
        # =====================================================

        query = (
            db.session.query(
                AuditFinding
            )

            # -------------------------------------------------
            # Finding
            # -------------------------------------------------

            .join(
                AuditExecution,
                AuditFinding.audit_execution_id
                == AuditExecution.id,
            )

            # -------------------------------------------------
            # Assignment
            # -------------------------------------------------

            .join(
                AuditAssignment,
                AuditExecution.audit_assignment_id
                == AuditAssignment.id,
            )

            # -------------------------------------------------
            # Audit
            # -------------------------------------------------

            .join(
                Audit,
                AuditAssignment.audit_id
                == Audit.id,
            )

            # -------------------------------------------------
            # Active records only
            # -------------------------------------------------

            .filter(
                AuditFinding.is_active.is_(True),

                AuditExecution.is_active.is_(True),

                AuditAssignment.is_active.is_(True),

                Audit.is_active.is_(True),
            )
        )


        # =====================================================
        # PERIOD FILTER
        #
        # IMPORTANT:
        #
        # Period Finding mengikuti Audit.audit_date
        # agar sama dengan periode Dashboard.
        #
        # Audit
        #   ↓
        # Assignment
        #   ↓
        # Execution
        #   ↓
        # Finding
        #
        # =====================================================

        if start_date and end_date:

            query = query.filter(

                Audit.audit_date
                >= start_date,

                Audit.audit_date
                <= end_date,

            )


        # =====================================================
        # SEARCH
        #
        # Search:
        # - Finding No
        # - Finding
        # - Audit No
        # - Audit Title
        # =====================================================

        if search:

            search_pattern = (
                f"%{search}%"
            )

            query = query.filter(

                or_(

                    AuditFinding.finding_no.ilike(
                        search_pattern
                    ),

                    AuditFinding.finding.ilike(
                        search_pattern
                    ),

                    Audit.audit_no.ilike(
                        search_pattern
                    ),

                    Audit.title.ilike(
                        search_pattern
                    ),

                )
            )


        # =====================================================
        # STATUS FILTER
        #
        # Exact status filter.
        #
        # Example:
        # status=OPEN
        # status=CLOSED
        # status=AUDITOR_VERIFICATION
        #
        # =====================================================

        if status:

            query = query.filter(

                AuditFinding.status
                == status

            )


        # =====================================================
        # OPEN FINDINGS FILTER
        #
        # Open Finding berarti:
        #
        # status != CLOSED
        #
        # Jadi termasuk:
        #
        # OPEN
        # IN_PROGRESS
        # ACTION_COMPLETED
        # AUDITOR_VERIFICATION
        # PASS
        #
        # =====================================================

        if open_only.lower() in [
            "1",
            "true",
            "yes",
            "open",
        ]:

            query = query.filter(

                AuditFinding.status
                != self.STATUS_CLOSED

            )


        # =====================================================
        # SEVERITY FILTER
        # =====================================================

        if severity:

            query = query.filter(

                AuditFinding.severity
                == severity

            )


        # =====================================================
        # FINDING SOURCE FILTER
        # =====================================================

        if finding_source:

            query = query.filter(

                AuditFinding.finding_source
                == finding_source

            )


        # =====================================================
        # DEPARTMENT FILTER
        #
        # Audit Finding
        #     ↓
        # Audit Execution
        #     ↓
        # Audit Assignment
        #     ↓
        # Department
        #
        # =====================================================

        if department_id:

            try:

                department_id_int = int(
                    department_id
                )

                query = query.filter(

                    AuditAssignment.department_id
                    == department_id_int

                )

            except (
                TypeError,
                ValueError,
            ):

                department_id = ""


        # =====================================================
        # PIC FILTER
        # =====================================================

        if pic_employee_id:

            try:

                pic_employee_id_int = int(
                    pic_employee_id
                )

                query = query.filter(

                    AuditFinding.pic_employee_id
                    == pic_employee_id_int

                )

            except (
                TypeError,
                ValueError,
            ):

                pic_employee_id = ""


        # =====================================================
        # OVERDUE FILTER
        #
        # Overdue:
        #
        # target_date < today
        #
        # AND
        #
        # status != CLOSED
        #
        # =====================================================

        if overdue.lower() in [
            "1",
            "true",
            "yes",
            "overdue",
        ]:

            today = date.today()

            query = query.filter(

                AuditFinding.target_date.isnot(None),

                AuditFinding.target_date
                < today,

                AuditFinding.status
                != self.STATUS_CLOSED,

            )


        # =====================================================
        # ORDER
        # =====================================================

        query = query.order_by(

            AuditFinding.target_date.asc(),

            AuditFinding.created_at.desc(),

            AuditFinding.id.desc(),

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
        # BUILD RESULT
        # =====================================================

        findings_data = []

        today = date.today()


        for finding in pagination.items:

            # =================================================
            # AUDIT EXECUTION
            # =================================================

            execution = (
                finding.audit_execution
            )


            # =================================================
            # AUDIT ASSIGNMENT
            # =================================================

            assignment = (

                execution.audit_assignment

                if execution

                else None

            )


            # =================================================
            # AUDIT
            # =================================================

            audit = (

                assignment.audit

                if assignment

                else None

            )


            # =================================================
            # DEPARTMENT
            # =================================================

            department = (

                assignment.department

                if assignment

                else None

            )


            # =================================================
            # PIC
            # =================================================

            pic_employee = (

                finding.pic_employee

                if finding.pic_employee_id

                else None

            )


            # =================================================
            # OVERDUE
            # =================================================

            is_overdue = (

                finding.target_date
                is not None

                and finding.target_date
                < today

                and finding.status
                != self.STATUS_CLOSED

            )


            # =================================================
            # AUDIT DATA
            # =================================================

            audit_data = {

                "id":
                    audit.id
                    if audit
                    else None,

                "audit_no":
                    audit.audit_no
                    if audit
                    else "-",

                "title":
                    audit.title
                    if audit
                    else "-",

                "audit_date":
                    audit.audit_date
                    if audit
                    else None,

                "audit_date_display":
                    self._format_date(
                        audit.audit_date
                    )
                    if audit
                    else "-",

            }


            # =================================================
            # DEPARTMENT DATA
            # =================================================

            department_data = {

                "id":
                    department.id
                    if department
                    else None,

                "code":
                    department.department_code
                    if department
                    else "-",

                "name":
                    department.department_name
                    if department
                    else "-",

            }


            # =================================================
            # PIC DATA
            # =================================================

            pic_data = {

                "id":
                    pic_employee.id
                    if pic_employee
                    else None,

                "employee_code":
                    getattr(
                        pic_employee,
                        "employee_code",
                        "-"
                    )
                    if pic_employee
                    else "-",

                "name":
                    getattr(
                        pic_employee,
                        "full_name",
                        "-"
                    )
                    if pic_employee
                    else "-",

            }


            # =================================================
            # EXECUTION DATA
            # =================================================

            execution_data = {

                "id":
                    execution.id
                    if execution
                    else None,

                "execution_date":
                    execution.execution_date
                    if execution
                    else None,

                "execution_date_display":
                    self._format_date(
                        execution.execution_date
                    )
                    if execution
                    else "-",

                "status":
                    execution.status
                    if execution
                    else "-",

            }


            # =================================================
            # FINDING DATA
            # =================================================

            findings_data.append({

                "id":
                    finding.id,

                "finding_no":
                    finding.finding_no,

                "finding":
                    finding.finding,

                "finding_source":
                    finding.finding_source,

                "severity":
                    finding.severity,

                "status":
                    finding.status,

                "target_date":
                    finding.target_date,

                "target_date_display":
                    self._format_date(
                        finding.target_date
                    ),

                "is_overdue":
                    is_overdue,

                "corrective_action":
                    finding.corrective_action,

                "action_completed_date":
                    finding.action_completed_date,

                "action_completed_date_display":
                    self._format_date(
                        finding.action_completed_date
                    ),

                "verification_status":
                    finding.verification_status,

                "verified_date":
                    finding.verified_date,

                "verified_date_display":
                    self._format_date(
                        finding.verified_date
                    ),

                "audit":
                    audit_data,

                "execution":
                    execution_data,

                "department":
                    department_data,

                "pic":
                    pic_data,

            })


        # =====================================================
        # MASTER DATA - DEPARTMENT
        # =====================================================

        departments = (

            db.session.query(
                Department
            )

            .filter(
                Department.is_active.is_(True)
            )

            .order_by(
                Department.department_name.asc()
            )

            .all()

        )


        # =====================================================
        # MASTER DATA - EMPLOYEE / PIC
        # =====================================================

        employees = (

            db.session.query(
                Employee
            )

            .filter(
                Employee.is_active.is_(True)
            )

            .order_by(
                Employee.full_name.asc()
            )

            .all()

        )


        # =====================================================
        # PERIOD DISPLAY
        # =====================================================

        if start_date and end_date:

            period_start_display = (
                start_date.strftime(
                    "%d %b %Y"
                )
            )

            period_end_display = (
                end_date.strftime(
                    "%d %b %Y"
                )
            )

        else:

            period_start_display = "-"
            period_end_display = "-"


        # =====================================================
        # RETURN
        # =====================================================

        return {

            "findings":
                findings_data,

            "pagination":
                pagination,

            "filters": {

                "search":
                    search,

                "status":
                    status,

                "severity":
                    severity,

                "finding_source":
                    finding_source,

                "department_id":
                    department_id,

                "pic_employee_id":
                    pic_employee_id,

                "overdue":
                    overdue,

                "open_only":
                    open_only,

                "period":
                    period,

            },

            "departments":
                departments,

            "employees":
                employees,

            "statuses": [

                self.STATUS_OPEN,

                self.STATUS_IN_PROGRESS,

                self.STATUS_ACTION_COMPLETED,

                self.STATUS_AUDITOR_VERIFICATION,

                self.STATUS_PASS,

                self.STATUS_CLOSED,

            ],

            "severities": [

                self.SEVERITY_CRITICAL,

                self.SEVERITY_MAJOR,

                self.SEVERITY_MINOR,

                self.SEVERITY_OBSERVATION,

            ],

            "finding_sources": [

                self.SOURCE_CHECKLIST,

                self.SOURCE_OUTSIDE_CHECKLIST,

            ],

            "period": {

                "start_date":
                    start_date,

                "end_date":
                    end_date,

                "start_date_display":
                    period_start_display,

                "end_date_display":
                    period_end_display,

            },

        }