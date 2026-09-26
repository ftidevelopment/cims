from datetime import datetime, timedelta
from app.models.kaizen import Kaizen
from app.repositories.base_repository import BaseRepository


class KaizenRepository(BaseRepository):
    """
    Repository untuk mengelola data Kaizen.
    """

    def __init__(self):
        super().__init__(Kaizen)

        # ==================================================
        # Searchable Fields
        # ==================================================

        self.searchable_fields = [
            Kaizen.kaizen_no,
            Kaizen.title,
            Kaizen.description,
            Kaizen.kaizen_category_id,
        ]

        # ==================================================
        # Sortable Fields
        # ==================================================

        self.sortable_fields = {
            "kaizen_no": Kaizen.kaizen_no,
            "title": Kaizen.title,
            "category": Kaizen.kaizen_category_id,
            "status": Kaizen.status,
            "created_at": Kaizen.created_at,
            "updated_at": Kaizen.updated_at,
        }


    # ==================================================
    # QUERY
    # ==================================================

    def get_query(
        self,
        keyword=None,
        status=None,
        department_id=None,
        date_from=None,
        date_to=None,
        employee_id=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):

        # ==================================================
        # Base Query
        # ==================================================

        query = super().get_query(
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )


        # ==================================================
        # Employee / My Kaizen
        # ==================================================

        if employee_id:

            query = query.filter(
                Kaizen.employee_id == employee_id
            )


        # ==================================================
        # Status Filter
        # ==================================================

        if status:

            query = query.filter(
                Kaizen.status == status
            )


        # ==================================================
        # Department Filter
        # ==================================================

        if department_id:

            query = query.filter(
                Kaizen.department_id == department_id
            )


        # ==================================================
        # Create Date - From
        # ==================================================

        if date_from:

            try:

                date_from_value = datetime.strptime(
                    date_from,
                    "%Y-%m-%d"
                )

                query = query.filter(
                    Kaizen.created_at >= date_from_value
                )

            except ValueError:

                pass


        # ==================================================
        # Create Date - To
        # ==================================================

        if date_to:

            try:

                date_to_value = datetime.strptime(
                    date_to,
                    "%Y-%m-%d"
                )

                # Include the entire To Date
                date_to_exclusive = (
                    date_to_value + timedelta(days=1)
                )

                query = query.filter(
                    Kaizen.created_at < date_to_exclusive
                )

            except ValueError:

                pass


        return query


    # ==================================================
    # GET ALL
    # ==================================================

    def get_all(
        self,
        keyword=None,
        status=None,
        department_id=None,
        date_from=None,
        date_to=None,
        employee_id=None,
        is_active=True,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="asc",
    ):

        query = self.get_query(

            keyword=keyword,

            status=status,

            department_id=department_id,

            date_from=date_from,

            date_to=date_to,

            employee_id=employee_id,

            is_active=is_active,

            sort_by=sort_by,

            sort_order=sort_order,
        )

        return query.paginate(

            page=page,

            per_page=per_page,

            error_out=False,
        )

    # ==================================================
    # FIND BY KAIZEN NO
    # ==================================================

    def find_by_kaizen_no(self, kaizen_no):
        return self.get_first_by(
            kaizen_no=kaizen_no
        )

    # ==================================================
    # FIND BY STATUS
    # ==================================================

    def find_by_status(self, status):
        return self.find_by(
            status=status
        )

    # ==================================================
    # FIND BY EMPLOYEE / PIC
    # ==================================================

    def find_by_employee(self, employee_id):
        return self.find_by(
            employee_id=employee_id
        )

    # ==================================================
    # FIND BY DEPARTMENT
    # ==================================================

    def find_by_department(self, department_id):
        return self.find_by(
            department_id=department_id
        )

    # ==================================================
    # FIND BY PROBLEM
    # ==================================================

    def find_by_problem(self, problem_id):
        return self.find_by(
            problem_id=problem_id
        )

    # ==================================================
    # FIND BY IMPROVEMENT
    # ==================================================

    def find_by_improvement(self, improvement_id):
        return self.find_by(
            improvement_id=improvement_id
        )

    # ==================================================
    # FIND BY STATUS AND DEPARTMENT
    # ==================================================

    def find_by_status_and_department(
        self,
        status,
        department_id
    ):
        return self.find_by(
            status=status,
            department_id=department_id
        )

    # ==================================================
    # WORKFLOW
    # ==================================================

    def find_draft(self):
        return self.find_by_status("Draft")

    def find_proposals(self):
        return self.find_by_status("Proposal")

    def find_approved(self):
        return self.find_by_status("Approved")

    def find_rejected(self):
        return self.find_by_status("Rejected")

    def find_implemented(self):
        return self.find_by_status("Implemented")

    # ==================================================
    # APPROVAL
    # ==================================================

    def find_by_approver(self, employee_id):
        return self.find_by(
            approved_by_employee_id=employee_id
        )

    # ==================================================
    # REJECTION
    # ==================================================

    def find_by_rejector(self, employee_id):
        return self.find_by(
            rejected_by_employee_id=employee_id
        )


    # ==================================================
    # FIND BY AWARD PERIOD
    # ==================================================

    def find_by_approved_date_range(
        self,
        start_date,
        end_date
    ):
        from datetime import datetime, time, timedelta

        start_datetime = datetime.combine(
            start_date,
            time.min
        )

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min
        )

        return (
            self.model.query
            .filter(
                self.model.is_active.is_(True),
                self.model.approved_at.isnot(None),
                self.model.approved_at >= start_datetime,
                self.model.approved_at < end_datetime
            )
            .order_by(
                self.model.approved_at.asc(),
                self.model.kaizen_no.asc()
            )
            .all()
        )