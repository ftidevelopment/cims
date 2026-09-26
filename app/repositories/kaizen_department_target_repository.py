from sqlalchemy import or_

from app.models.kaizen_department_target import (
    KaizenDepartmentTarget
)

from app.models.kaizen_reporting_period import (
    KaizenReportingPeriod
)

from app.models.department import Department

from app.repositories.base_repository import BaseRepository


class KaizenDepartmentTargetRepository(BaseRepository):

    model = KaizenDepartmentTarget

    searchable_fields = [
        KaizenDepartmentTarget.description,
    ]

    sortable_fields = {
        "target_quantity":
            KaizenDepartmentTarget.target_quantity,

        "created_at":
            KaizenDepartmentTarget.created_at,

        "updated_at":
            KaizenDepartmentTarget.updated_at,
    }

    def __init__(self):
        super().__init__(
            KaizenDepartmentTarget
        )

    # =========================================================
    # GET ALL
    # =========================================================

    def get_all(
        self,
        keyword=None,
        is_active=True,
        department_id=None,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="asc"
    ):

        query = (
            self.model.query
            .join(
                KaizenReportingPeriod,
                KaizenDepartmentTarget.reporting_period_id
                == KaizenReportingPeriod.id
            )
            .join(
                Department,
                KaizenDepartmentTarget.department_id
                == Department.id
            )
        )

        # =====================================================
        # STATUS
        # =====================================================

        if is_active is not None:

            query = query.filter(
                KaizenDepartmentTarget.is_active
                == is_active
            )

        # =====================================================
        # DEPARTMENT FILTER
        # =====================================================

        if department_id is not None:

            query = query.filter(
                KaizenDepartmentTarget.department_id
                == department_id
            )

        # =====================================================
        # SEARCH
        # =====================================================

        if keyword:

            search = f"%{keyword.strip()}%"

            query = query.filter(
                or_(
                    KaizenReportingPeriod.period_code.ilike(
                        search
                    ),

                    KaizenReportingPeriod.period_name.ilike(
                        search
                    ),

                    Department.department_code.ilike(
                        search
                    ),

                    Department.department_name.ilike(
                        search
                    ),

                    KaizenDepartmentTarget.description.ilike(
                        search
                    ),
                )
            )

        # =====================================================
        # SORT
        # =====================================================

        sort_mapping = {

            "reporting_period":
                KaizenReportingPeriod.period_name,

            "department":
                Department.department_name,

            "target_quantity":
                KaizenDepartmentTarget.target_quantity,

            "description":
                KaizenDepartmentTarget.description,

            "created_at":
                KaizenDepartmentTarget.created_at,

            "updated_at":
                KaizenDepartmentTarget.updated_at,
        }

        sort_column = sort_mapping.get(
            sort_by,
            KaizenDepartmentTarget.created_at
        )

        if sort_order == "asc":

            query = query.order_by(
                sort_column.asc()
            )

        else:

            query = query.order_by(
                sort_column.desc()
            )

        # =====================================================
        # PAGINATION
        # =====================================================

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    # =========================================================
    # GET BY PERIOD AND DEPARTMENT
    # =========================================================

    def get_by_period_and_department(
        self,
        reporting_period_id,
        department_id
    ):

        return self.get_first_by(
            reporting_period_id=reporting_period_id,
            department_id=department_id
        )

    # =========================================================
    # EXISTS BY PERIOD AND DEPARTMENT
    # =========================================================

    def exists_by_period_and_department(
        self,
        reporting_period_id,
        department_id
    ):

        return (
            self.get_by_period_and_department(
                reporting_period_id,
                department_id
            )
            is not None
        )

    # =========================================================
    # GET BY REPORTING PERIOD
    # =========================================================

    def get_by_reporting_period(
        self,
        reporting_period_id
    ):

        return self.find_by(
            reporting_period_id=reporting_period_id
        )

    # =========================================================
    # GET BY DEPARTMENT
    # =========================================================

    def get_by_department(
        self,
        department_id
    ):

        return self.find_by(
            department_id=department_id
        )

    # =========================================================
    # GET QUERY
    # =========================================================

    def get_query(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc"
    ):

        query = (
            self.model.query
            .join(
                KaizenReportingPeriod,
                KaizenDepartmentTarget.reporting_period_id
                == KaizenReportingPeriod.id
            )
            .join(
                Department,
                KaizenDepartmentTarget.department_id
                == Department.id
            )
        )

        # =====================================================
        # STATUS
        # =====================================================

        if is_active is not None:

            query = query.filter(
                KaizenDepartmentTarget.is_active
                == is_active
            )

        # =====================================================
        # SEARCH
        # =====================================================

        if keyword:

            search = f"%{keyword.strip()}%"

            query = query.filter(
                or_(
                    KaizenReportingPeriod.period_code.ilike(
                        search
                    ),

                    KaizenReportingPeriod.period_name.ilike(
                        search
                    ),

                    Department.department_code.ilike(
                        search
                    ),

                    Department.department_name.ilike(
                        search
                    ),

                    KaizenDepartmentTarget.description.ilike(
                        search
                    ),
                )
            )

        # =====================================================
        # SORT
        # =====================================================

        sort_mapping = {

            "reporting_period":
                KaizenReportingPeriod.period_name,

            "department":
                Department.department_name,

            "target_quantity":
                KaizenDepartmentTarget.target_quantity,

            "description":
                KaizenDepartmentTarget.description,

            "created_at":
                KaizenDepartmentTarget.created_at,

            "updated_at":
                KaizenDepartmentTarget.updated_at,
        }

        sort_column = sort_mapping.get(
            sort_by,
            KaizenDepartmentTarget.created_at
        )

        if sort_order == "asc":

            query = query.order_by(
                sort_column.asc()
            )

        else:

            query = query.order_by(
                sort_column.desc()
            )

        return query