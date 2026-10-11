from datetime import date

from sqlalchemy import or_

from app.extensions import db

from app.models.audit import Audit
from app.models.audit_assignment import AuditAssignment
from app.models.audit_execution import AuditExecution
from app.models.audit_finding import AuditFinding
from app.models.audit_type import AuditType
from app.models.audit_category import AuditCategory
from app.models.department import Department


class PublicAuditListService:
    """
    Public Audit List Service.

    Menyediakan data Audit untuk public dashboard/list.

    Features:
    - Pagination
    - Search
    - Status filter
    - Audit Type filter
    - Audit Category filter
    - Department filter
    - Period filter
    """

    # =========================================================
    # PERIOD
    # =========================================================

    def get_period(self):
        """
        Get default dashboard/list period.

        Default:
        6 bulan terakhir termasuk bulan berjalan.
        """

        today = date.today()

        start_date = (
            today.replace(day=1)
            - __import__(
                "dateutil.relativedelta",
                fromlist=["relativedelta"]
            ).relativedelta(
                months=5
            )
        )

        end_date = today

        return {
            "start_date": start_date,
            "end_date": end_date,
        }

    # =========================================================
    # GET AUDITS
    # =========================================================

    def get_audits(
        self,
        page=1,
        per_page=10,
        search="",
        status="",
        audit_type_id="",
        audit_category_id="",
        department_id="",
        period="",
        next_audit="",
        completed_audit="",
    ):
        """
        Get paginated public Audit list.

        Filter:
        - Search
        - Status
        - Audit Type
        - Audit Category
        - Department
        - Period
        - Next Audit
        - Completed Audit
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
        # NORMALIZE SEARCH
        # =====================================================

        search = (
            search.strip()
            if search
            else ""
        )


        # =====================================================
        # NORMALIZE STATUS
        # =====================================================

        status = (
            status.strip()
            if status
            else ""
        )


        # =====================================================
        # NORMALIZE AUDIT TYPE
        # =====================================================

        audit_type_id = (
            str(audit_type_id).strip()
            if audit_type_id
            else ""
        )


        # =====================================================
        # NORMALIZE AUDIT CATEGORY
        # =====================================================

        audit_category_id = (
            str(audit_category_id).strip()
            if audit_category_id
            else ""
        )


        # =====================================================
        # NORMALIZE DEPARTMENT
        # =====================================================

        department_id = (
            str(department_id).strip()
            if department_id
            else ""
        )


        # =====================================================
        # NORMALIZE PERIOD
        # =====================================================

        period = (
            period.strip()
            if period
            else ""
        )


        # =====================================================
        # NORMALIZE NEXT AUDIT
        # =====================================================

        next_audit = (
            str(next_audit).strip()
            if next_audit
            else ""
        )


        # =====================================================
        # NORMALIZE COMPLETED AUDIT
        # =====================================================

        completed_audit = (
            str(completed_audit).strip()
            if completed_audit
            else ""
        )


        # =====================================================
        # PERIOD
        # =====================================================

        default_period = self.get_period()

        start_date = (
            default_period["start_date"]
        )

        end_date = (
            default_period["end_date"]
        )


        # =====================================================
        # ALL PERIOD
        # =====================================================

        if period.lower() == "all":

            start_date = None
            end_date = None


        # =====================================================
        # TODAY
        # =====================================================

        today = date.today()


        # =====================================================
        # BASE QUERY
        # =====================================================

        query = (
            db.session.query(Audit)
            .filter(
                Audit.is_active.is_(True)
            )
        )


        # =====================================================
        # PERIOD FILTER
        #
        # Default:
        # Last 6 months
        #
        # ALL:
        # No date filter
        #
        # NEXT AUDIT:
        # Ignore normal period filter
        # =====================================================

        if (
            start_date
            and end_date
            and next_audit != "1"
        ):

            query = query.filter(

                Audit.audit_date >= start_date,

                Audit.audit_date <= end_date,

            )


        # =====================================================
        # NEXT AUDIT
        #
        # Audit date > today
        # Status must not be CANCELLED
        #
        # Example:
        #
        # Today      : 07-10-2026
        # Audit Date : 28-10-2026
        #
        # Result:
        # Next Audit
        # =====================================================

        if next_audit == "1":

            query = query.filter(

                Audit.audit_date > today,

                Audit.status != "CANCELLED",

            )


        # =====================================================
        # COMPLETED AUDIT
        #
        # Audit date <= today
        # Status = COMPLETED
        # =====================================================

        if completed_audit == "1":

            query = query.filter(

                Audit.audit_date <= today,

                Audit.status == "COMPLETED",

            )


        # =====================================================
        # SEARCH
        #
        # Search:
        # - Audit No
        # - Title
        # - Description
        # =====================================================

        if search:

            search_pattern = (
                f"%{search}%"
            )

            query = query.filter(

                or_(

                    Audit.audit_no.ilike(
                        search_pattern
                    ),

                    Audit.title.ilike(
                        search_pattern
                    ),

                    Audit.description.ilike(
                        search_pattern
                    ),

                )

            )


        # =====================================================
        # STATUS FILTER
        # =====================================================

        if status:

            query = query.filter(

                Audit.status == status

            )


        # =====================================================
        # AUDIT TYPE FILTER
        # =====================================================

        if audit_type_id:

            try:

                audit_type_id_int = int(
                    audit_type_id
                )

                query = query.filter(

                    Audit.audit_type_id
                    == audit_type_id_int

                )

            except (
                TypeError,
                ValueError
            ):

                pass


        # =====================================================
        # AUDIT CATEGORY FILTER
        # =====================================================

        if audit_category_id:

            try:

                audit_category_id_int = int(
                    audit_category_id
                )

                query = query.filter(

                    Audit.audit_category_id
                    == audit_category_id_int

                )

            except (
                TypeError,
                ValueError
            ):

                pass


        # =====================================================
        # DEPARTMENT FILTER
        #
        # Audit
        #   ↓
        # AuditAssignment
        #   ↓
        # Department
        # =====================================================

        if department_id:

            try:

                department_id_int = int(
                    department_id
                )

                query = query.filter(

                    Audit.assignments.any(

                        AuditAssignment.department_id
                        == department_id_int

                    )

                )

            except (
                TypeError,
                ValueError
            ):

                pass


        # =====================================================
        # ORDER
        #
        # Next Audit:
        # nearest future audit first
        #
        # Normal:
        # newest audit first
        # =====================================================

        if next_audit == "1":

            query = query.order_by(

                Audit.audit_date.asc(),

                Audit.id.asc(),

            )

        else:

            query = query.order_by(

                Audit.audit_date.desc(),

                Audit.id.desc(),

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
        # BUILD LIST DATA
        # =====================================================

        audits_data = []


        for audit in pagination.items:


            # =================================================
            # ASSIGNMENTS
            # =================================================

            assignments = (
                audit.audit_assignments
                or []
            )


            # =================================================
            # DEPARTMENTS
            # =================================================

            departments = []

            department_ids = set()


            for assignment in assignments:

                department = (
                    assignment.department
                )


                if (
                    department
                    and department.id
                    not in department_ids
                ):

                    departments.append(

                        {

                            "id":
                                department.id,

                            "code":
                                department.department_code,

                            "name":
                                department.department_name,

                        }

                    )

                    department_ids.add(
                        department.id
                    )


            # =================================================
            # EXECUTIONS
            # =================================================

            executions = []


            for assignment in assignments:

                for execution in (
                    assignment.audit_executions
                    or []
                ):

                    executions.append(
                        execution
                    )


            # =================================================
            # FINDINGS
            # =================================================

            findings = []


            for execution in executions:

                findings.extend(

                    execution.findings
                    or []

                )


            # =================================================
            # FINDING KPI
            # =================================================

            total_findings = len(
                findings
            )


            open_findings = sum(

                1

                for finding in findings

                if finding.status != "CLOSED"

            )


            closed_findings = sum(

                1

                for finding in findings

                if finding.status == "CLOSED"

            )


            overdue_findings = sum(

                1

                for finding in findings

                if (

                    finding.target_date

                    and finding.target_date < today

                    and finding.status != "CLOSED"

                )

            )


            verification_pending = sum(

                1

                for finding in findings

                if (
                    finding.status
                    == "AUDITOR_VERIFICATION"
                )

            )


            # =================================================
            # EXECUTION KPI
            # =================================================

            total_executions = len(
                executions
            )


            completed_executions = sum(

                1

                for execution in executions

                if execution.status
                == "COMPLETED"

            )


            # =================================================
            # AUDIT TYPE
            # =================================================

            audit_type = (
                audit.audit_type
            )


            # =================================================
            # AUDIT CATEGORY
            # =================================================

            audit_category = (
                audit.audit_category
            )


            # =================================================
            # APPEND DATA
            # =================================================

            audits_data.append(

                {

                    "id":
                        audit.id,

                    "audit_no":
                        audit.audit_no,

                    "title":
                        audit.title,

                    "description":
                        audit.description,

                    "audit_date":
                        audit.audit_date,

                    "status":
                        audit.status,


                    # -----------------------------------------
                    # AUDIT TYPE
                    # -----------------------------------------

                    "audit_type": (

                        {

                            "id":
                                audit_type.id,

                            "code":
                                audit_type.audit_type_code,

                            "name":
                                audit_type.audit_type_name,

                        }

                        if audit_type

                        else None

                    ),


                    # -----------------------------------------
                    # AUDIT CATEGORY
                    # -----------------------------------------

                    "audit_category": (

                        {

                            "id":
                                audit_category.id,

                            "code":
                                audit_category.audit_category_code,

                            "name":
                                audit_category.audit_category_name,

                        }

                        if audit_category

                        else None

                    ),


                    # -----------------------------------------
                    # DEPARTMENTS
                    # -----------------------------------------

                    "departments":
                        departments,


                    # -----------------------------------------
                    # ASSIGNMENTS
                    # -----------------------------------------

                    "assignment_count":
                        len(assignments),


                    # -----------------------------------------
                    # EXECUTIONS
                    # -----------------------------------------

                    "execution_count":
                        total_executions,

                    "completed_execution_count":
                        completed_executions,


                    # -----------------------------------------
                    # FINDINGS
                    # -----------------------------------------

                    "total_findings":
                        total_findings,

                    "open_findings":
                        open_findings,

                    "closed_findings":
                        closed_findings,

                    "overdue_findings":
                        overdue_findings,

                    "verification_pending":
                        verification_pending,

                }

            )


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
        # MASTER DATA - AUDIT TYPE
        # =====================================================

        audit_types = (

            db.session.query(
                AuditType
            )

            .filter(
                AuditType.is_active.is_(True)
            )

            .order_by(
                AuditType.audit_type_name.asc()
            )

            .all()

        )


        # =====================================================
        # MASTER DATA - AUDIT CATEGORY
        # =====================================================

        audit_categories = (

            db.session.query(
                AuditCategory
            )

            .filter(
                AuditCategory.is_active.is_(True)
            )

            .order_by(
                AuditCategory.audit_category_name.asc()
            )

            .all()

        )


        # =====================================================
        # RETURN
        # =====================================================

        return {

            "audits":
                audits_data,

            "pagination":
                pagination,

            "filters": {

                "search":
                    search,

                "status":
                    status,

                "audit_type_id":
                    audit_type_id,

                "audit_category_id":
                    audit_category_id,

                "department_id":
                    department_id,

                "period":
                    period,

                "next_audit":
                    next_audit,

                "completed_audit":
                    completed_audit,

            },

            "departments":
                departments,

            "audit_types":
                audit_types,

            "audit_categories":
                audit_categories,

            "period": {

                "start_date":
                    start_date,

                "end_date":
                    end_date,

            },

            "per_page":
                per_page,

        }