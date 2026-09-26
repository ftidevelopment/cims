from datetime import (
    date,
    datetime,
    timedelta,
)

from dateutil.relativedelta import relativedelta

from sqlalchemy import or_

from app.extensions import db

from app.models.kaizen import Kaizen
from app.models.department import Department


class PublicKaizenListService:

    # =========================================================
    # FORMAT DATE
    # =========================================================

    def _format_date(self, value):

        if not value:
            return "-"

        # -----------------------------------------------------
        # Already string
        # -----------------------------------------------------

        if isinstance(value, str):

            try:

                parsed_date = datetime.fromisoformat(
                    value
                )

                return parsed_date.strftime(
                    "%d-%m-%Y"
                )

            except ValueError:

                return value

        # -----------------------------------------------------
        # datetime / date
        # -----------------------------------------------------

        return value.strftime(
            "%d-%m-%Y"
        )


    # =========================================================
    # GET KAIZENS
    # =========================================================

    def get_kaizens(
        self,
        page=1,
        per_page=10,
        search="",
        status="",
        department_id="",
        period="",
        open_only=False,
        aging="",
    ):

        # =====================================================
        # NORMALIZE
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

        department_id = (
            department_id.strip()
            if department_id
            else ""
        )

        period = (
            period.strip()
            if period
            else ""
        )

        aging = (
            aging.strip()
            if aging
            else ""
        )

        # =====================================================
        # NORMALIZE BOOLEAN
        # =====================================================

        if isinstance(open_only, str):

            open_only = (
                open_only.lower()
                == "true"
            )

        else:

            open_only = bool(
                open_only
            )


        # =====================================================
        # DATE RANGE
        # =====================================================

        today = date.today()

        # -----------------------------------------------------
        # Last 6 months
        #
        # Example September 2026:
        #
        # Start = 01 April 2026
        # End   = today
        # -----------------------------------------------------

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today


        # =====================================================
        # DATETIME RANGE
        # =====================================================

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

        query = (
            db.session.query(
                Kaizen
            )
            .filter(
                Kaizen.is_active.is_(True)
            )
        )


        # =====================================================
        # PERIOD FILTER
        # =====================================================

        if period == "6_months":

            query = query.filter(

                Kaizen.created_at
                >= start_datetime,

                Kaizen.created_at
                < end_datetime,

            )


        # =====================================================
        # OPEN / PENDING
        #
        # Same definition used by Dashboard:
        #
        # Approved = NULL
        # Rejected = NULL
        #
        # Therefore the Kaizen is still open/pending.
        # =====================================================

        if open_only:

            query = query.filter(

                Kaizen.approved_at.is_(None),

                Kaizen.rejected_at.is_(None),

            )


        # =====================================================
        # AGING
        #
        # Aging is calculated from:
        #
        # today - created_at
        #
        # Only open/pending Kaizen are included.
        # =====================================================

        if aging:

            # -------------------------------------------------
            # Aging only applies to open Kaizen
            # -------------------------------------------------

            query = query.filter(

                Kaizen.approved_at.is_(None),

                Kaizen.rejected_at.is_(None),

            )


            # -------------------------------------------------
            # 0 - 7 Days
            # -------------------------------------------------

            if aging == "0_7":

                aging_start = datetime.combine(
                    today - timedelta(days=7),
                    datetime.min.time(),
                )

                aging_end = end_datetime

                query = query.filter(

                    Kaizen.created_at
                    >= aging_start,

                    Kaizen.created_at
                    < aging_end,

                )


            # -------------------------------------------------
            # 8 - 14 Days
            # -------------------------------------------------

            elif aging == "8_14":

                aging_start = datetime.combine(
                    today - timedelta(days=14),
                    datetime.min.time(),
                )

                aging_end = datetime.combine(
                    today - timedelta(days=7),
                    datetime.min.time(),
                )

                query = query.filter(

                    Kaizen.created_at
                    >= aging_start,

                    Kaizen.created_at
                    < aging_end,

                )


            # -------------------------------------------------
            # 15 - 30 Days
            # -------------------------------------------------

            elif aging == "15_30":

                aging_start = datetime.combine(
                    today - timedelta(days=30),
                    datetime.min.time(),
                )

                aging_end = datetime.combine(
                    today - timedelta(days=14),
                    datetime.min.time(),
                )

                query = query.filter(

                    Kaizen.created_at
                    >= aging_start,

                    Kaizen.created_at
                    < aging_end,

                )


            # -------------------------------------------------
            # 31 - 60 Days
            # -------------------------------------------------

            elif aging == "31_60":

                aging_start = datetime.combine(
                    today - timedelta(days=60),
                    datetime.min.time(),
                )

                aging_end = datetime.combine(
                    today - timedelta(days=30),
                    datetime.min.time(),
                )

                query = query.filter(

                    Kaizen.created_at
                    >= aging_start,

                    Kaizen.created_at
                    < aging_end,

                )


            # -------------------------------------------------
            # > 60 Days
            # -------------------------------------------------

            elif aging == "over_60":

                aging_end = datetime.combine(
                    today - timedelta(days=60),
                    datetime.min.time(),
                )

                query = query.filter(

                    Kaizen.created_at
                    < aging_end

                )


        # =====================================================
        # SEARCH
        # =====================================================

        if search:

            keyword = (
                f"%{search}%"
            )

            query = query.filter(

                or_(

                    Kaizen.kaizen_no.ilike(
                        keyword
                    ),

                    Kaizen.title.ilike(
                        keyword
                    ),

                    Kaizen.description.ilike(
                        keyword
                    ),

                )

            )


        # =====================================================
        # STATUS
        # =====================================================

        if status:

            query = query.filter(

                Kaizen.status == status

            )


        # =====================================================
        # DEPARTMENT
        # =====================================================

        if department_id:

            try:

                department_id_int = int(
                    department_id
                )

                query = query.filter(

                    Kaizen.department_id
                    == department_id_int

                )

            except (
                TypeError,
                ValueError,
            ):

                department_id = ""


        # =====================================================
        # ORDER
        # =====================================================

        query = query.order_by(

            Kaizen.created_at.desc(),

            Kaizen.id.desc(),

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

        kaizens = []


        for item in pagination.items:

            # -------------------------------------------------
            # Department
            # -------------------------------------------------

            if item.department:

                department_name = (
                    item.department.department_name
                )

            else:

                department_name = "-"


            # -------------------------------------------------
            # Employee
            # -------------------------------------------------

            if item.employee:

                employee_name = (
                    item.employee.full_name
                )

            else:

                employee_name = "-"


            # -------------------------------------------------
            # Category
            # -------------------------------------------------

            category_name = "-"


            if getattr(
                item,
                "kaizen_category",
                None,
            ):

                category_name = (
                    item.kaizen_category
                    .kaizen_category_name
                )


            # -------------------------------------------------
            # Created Date
            # -------------------------------------------------

            created_at_display = (
                self._format_date(
                    item.created_at
                )
            )


            # -------------------------------------------------
            # Implementation Date
            # -------------------------------------------------

            implementation_date_display = (
                self._format_date(
                    item.implementation_date
                )
            )


            # -------------------------------------------------
            # Cost Saving
            # -------------------------------------------------

            cost_saving = float(
                item.cost_saving or 0
            )


            # -------------------------------------------------
            # Append
            # -------------------------------------------------

            kaizens.append(

                {

                    "id":
                        item.id,

                    "kaizen_no":
                        item.kaizen_no,

                    "title":
                        item.title,

                    "description":
                        item.description,

                    "category":
                        category_name,

                    "employee":
                        employee_name,

                    "department":
                        department_name,

                    "department_id":
                        item.department_id,

                    "status":
                        item.status or "-",

                    "created_at":
                        item.created_at,

                    "created_at_display":
                        created_at_display,

                    "implementation_date":
                        item.implementation_date,

                    "implementation_date_display":
                        implementation_date_display,

                    "cost_saving":
                        cost_saving,

                    "approved_at":
                        item.approved_at,

                    "rejected_at":
                        item.rejected_at,

                }

            )


        # =====================================================
        # DEPARTMENT LIST
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
        # PERIOD DISPLAY
        # =====================================================

        if period == "6_months":

            period_start = start_date

            period_end = end_date

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

            period_start = None

            period_end = None

            period_start_display = ""

            period_end_display = ""


        # =====================================================
        # RETURN
        # =====================================================

        return {

            # -------------------------------------------------
            # Data
            # -------------------------------------------------

            "kaizens":
                kaizens,

            "pagination":
                pagination,


            # -------------------------------------------------
            # Filters
            # -------------------------------------------------

            "search":
                search,

            "status":
                status,

            "department_id":
                department_id,

            "departments":
                departments,

            "period":
                period,


            # -------------------------------------------------
            # Period
            # -------------------------------------------------

            "period_start":
                period_start,

            "period_end":
                period_end,

            "period_start_display":
                period_start_display,

            "period_end_display":
                period_end_display,


            # -------------------------------------------------
            # Open / Aging
            # -------------------------------------------------

            "open_only":
                open_only,

            "aging":
                aging,

        }