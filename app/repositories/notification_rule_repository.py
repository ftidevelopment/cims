from sqlalchemy import or_

from app.models.notification_rule import NotificationRule
from app.models.employee import Employee
from app.repositories.base_repository import BaseRepository


class NotificationRuleRepository(BaseRepository):
    """
    Repository for notification rule operations.
    """

    def __init__(self):

        super().__init__(
            model=NotificationRule
        )


    # ==================================================
    # QUERY
    # ==================================================

    def get_query(
        self,
        keyword=None,
        module=None,
        event=None,
        department_id=None,
        is_active=True,
    ):

        # ==================================================
        # Base Query
        # ==================================================

        query = super().get_query(
            keyword=None,
            is_active=is_active,
        )


        # ==================================================
        # Join Employee
        #
        # Digunakan untuk Employee Search
        # ==================================================

        query = query.join(
            Employee,
            NotificationRule.employee_id == Employee.id
        )


        # ==================================================
        # Employee Search
        #
        # Keyword hanya mencari:
        # - Employee Name
        # - Employee NIK
        # ==================================================

        if keyword:

            search_keyword = f"%{keyword}%"

            query = query.filter(
                or_(
                    Employee.full_name.ilike(
                        search_keyword
                    ),

                    Employee.nik.ilike(
                        search_keyword
                    ),
                )
            )


        # ==================================================
        # Module Filter
        # ==================================================

        if module:

            query = query.filter(
                NotificationRule.module == module
            )


        # ==================================================
        # Event Filter
        # ==================================================

        if event:

            query = query.filter(
                NotificationRule.event == event
            )


        # ==================================================
        # Department Filter
        # ==================================================

        if department_id:

            query = query.filter(
                NotificationRule.department_id
                == department_id
            )


        return query


    # ==================================================
    # GET ALL
    # ==================================================

    def get_all(
        self,
        keyword=None,
        module=None,
        event=None,
        department_id=None,
        is_active=True,
        page=1,
        per_page=10,
    ):

        query = self.get_query(

            keyword=keyword,

            module=module,

            event=event,

            department_id=department_id,

            is_active=is_active,
        )


        return query.paginate(

            page=page,

            per_page=per_page,

            error_out=False,
        )


    # ==================================================
    # GET BY EVENT
    # ==================================================

    def get_by_event(
        self,
        module,
        event,
        department_id,
    ):

        """
        Get active notification rules
        for a specific module, event,
        and department.
        """

        return (
            self.model.query
            .filter_by(
                module=module,
                event=event,
                department_id=department_id,
                is_active=True,
            )
            .all()
        )


    # ==================================================
    # EXISTS RULE
    # ==================================================

    def exists_rule(
        self,
        module,
        event,
        department_id,
        employee_id,
    ):

        """
        Check whether a notification rule
        already exists.
        """

        return (
            self.model.query
            .filter_by(
                module=module,
                event=event,
                department_id=department_id,
                employee_id=employee_id,
            )
            .first()
            is not None
        )


    # ==================================================
    # HARD DELETE
    # ==================================================

    def hard_delete(self, entity):

        """
        Permanently delete a notification rule.
        """

        from app.extensions import db

        db.session.delete(entity)