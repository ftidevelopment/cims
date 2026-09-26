from app.core.transaction_manager import (
    TransactionManager,
)

from app.models.notification_rule import (
    NotificationRule,
)

from app.repositories.notification_rule_repository import (
    NotificationRuleRepository,
)

from app.repositories.employee_repository import (
    EmployeeRepository,
)

from app.repositories.department_repository import (
    DepartmentRepository,
)

from app.services.base_service import (
    BaseService,
)

from app.core.notification_events import (
    NotificationEvent,
)

class NotificationRuleService(BaseService):
    """
    Service for managing notification rules.
    """

    # ==========================================
    # Notification Modules
    # ==========================================

    VALID_MODULES = (
        NotificationEvent.get_modules()
    )

    VALID_EVENTS = sorted({
        event
        for events in NotificationEvent.EVENTS.values()
        for event in events
    })

    def __init__(self):

        super().__init__()

        self.repository = (
            NotificationRuleRepository()
        )

        self.employee_repository = (
            EmployeeRepository()
        )

        self.department_repository = (
            DepartmentRepository()
        )

    # ==========================================
    # Get All
    # ==========================================

    def get_all(
        self,
        keyword=None,
        module=None,
        event=None,
        department_id=None,
        page=1,
        per_page=10,
    ):

        return self.repository.get_all(
            keyword=keyword,
            module=module,
            event=event,
            department_id=department_id,
            is_active=True,
            page=page,
            per_page=per_page,
        )

    # ==========================================
    # Get By ID
    # ==========================================

    def get_by_id(
        self,
        rule_id,
    ):

        return self.repository.get_by_id(
            rule_id
        )

    # ==========================================
    # Create
    # ==========================================

    def create(
        self,
        module,
        event,
        department_id,
        employee_id,
        email_enabled=True,
        line_enabled=False,
        created_by=None,
    ):

        try:

            # ==========================================
            # Validate Module
            # ==========================================

            self._validate_module(
                module
            )

            # ==========================================
            # Validate Event
            # ==========================================

            self._validate_event(
                event
            )

            # ==========================================
            # Validate Channels
            # ==========================================

            self._validate_channels(
                email_enabled,
                line_enabled,
            )

            # ==========================================
            # Validate Department
            # ==========================================

            department = (
                self.department_repository.get_by_id(
                    department_id
                )
            )

            if not department:

                return self.failed(
                    "Department not found."
                )

            # ==========================================
            # Validate Employee
            # ==========================================

            employee = (
                self.employee_repository.get_by_id(
                    employee_id
                )
            )

            if not employee:

                return self.failed(
                    "Employee not found."
                )

            # ==========================================
            # Validate Employee Status
            # ==========================================

            if employee.status != "ACTIVE":

                return self.failed(
                    "Employee is not active."
                )

            # ==========================================
            # Validate Employee Department
            # ==========================================

            # if (
            #     employee.department_id
            #     != department_id
            # ):

            #     return self.failed(
            #         "Employee does not belong "
            #         "to the selected department."
            #     )

            # ==========================================
            # Validate Email
            # ==========================================

            if email_enabled:

                if not employee.email:

                    return self.failed(
                        "Selected employee does not "
                        "have an email address."
                    )

            # ==========================================
            # Validate LINE
            # ==========================================

            if line_enabled:

                if not employee.line_user_id:

                    return self.failed(
                        "Selected employee does not "
                        "have a LINE User ID."
                    )

            # ==========================================
            # Validate Duplicate
            # ==========================================

            if self.repository.exists_rule(
                module=module,
                event=event,
                department_id=department_id,
                employee_id=employee_id,
            ):

                return self.failed(
                    "Notification rule already exists."
                )

            # ==========================================
            # Create Entity
            # ==========================================

            rule = NotificationRule(
                module=module,
                event=event,
                department_id=department_id,
                employee_id=employee_id,
                email_enabled=email_enabled,
                line_enabled=line_enabled,
                created_by=created_by,
            )

            # ==========================================
            # Save
            # ==========================================

            with TransactionManager():

                self.repository.create(
                    rule
                )

            return self.success(
                "Notification rule created successfully.",
                rule,
            )

        except ValueError as ex:

            return self.failed(
                str(ex)
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Update
    # ==========================================

    def update(
        self,
        rule_id,
        email_enabled,
        line_enabled,
        updated_by=None,
    ):

        try:

            # ==========================================
            # Validate Channels
            # ==========================================

            self._validate_channels(
                email_enabled,
                line_enabled,
            )

            # ==========================================
            # Get Rule
            # ==========================================

            rule = (
                self.repository.get_by_id(
                    rule_id
                )
            )

            if not rule:

                return self.failed(
                    "Notification rule not found."
                )

            # ==========================================
            # Validate Employee
            # ==========================================

            employee = (
                self.employee_repository.get_by_id(
                    rule.employee_id
                )
            )

            if not employee:

                return self.failed(
                    "Employee not found."
                )

            # ==========================================
            # Validate Email
            # ==========================================

            if email_enabled:

                if not employee.email:

                    return self.failed(
                        "Selected employee does not "
                        "have an email address."
                    )

            # ==========================================
            # Validate LINE
            # ==========================================

            if line_enabled:

                if not employee.line_user_id:

                    return self.failed(
                        "Selected employee does not "
                        "have a LINE User ID."
                    )

            # ==========================================
            # Update
            # ==========================================

            rule.email_enabled = (
                email_enabled
            )

            rule.line_enabled = (
                line_enabled
            )

            rule.updated_by = (
                updated_by
            )

            with TransactionManager():

                self.repository.update(
                    rule
                )

            return self.success(
                "Notification rule updated successfully.",
                rule,
            )

        except ValueError as ex:

            return self.failed(
                str(ex)
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Delete
    # ==========================================

    def delete(
        self,
        rule_id,
    ):
        """
        Permanently delete a notification rule.
        """

        try:

            rule = (
                self.repository.get_by_id(
                    rule_id
                )
            )

            if not rule:

                return self.failed(
                    "Notification rule not found."
                )

            with TransactionManager():

                self.repository.hard_delete(
                    rule
                )

            return self.success(
                "Notification rule deleted successfully."
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Restore
    # ==========================================

    def restore(
        self,
        rule_id,
        updated_by=None,
    ):

        try:

            rule = (
                self.repository.restore(
                    rule_id
                )
            )

            if not rule:

                return self.failed(
                    "Notification rule not found."
                )

            rule.updated_by = (
                updated_by
            )

            with TransactionManager():

                self.repository.update(
                    rule
                )

            return self.success(
                "Notification rule restored successfully.",
                rule,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Validation
    # ==========================================

    @classmethod
    def _validate_module(
        cls,
        module,
    ):

        if module not in cls.VALID_MODULES:

            raise ValueError(
                f"Invalid notification module: {module}"
            )

    @classmethod
    def _validate_event(
        cls,
        event,
    ):

        if event not in cls.VALID_EVENTS:

            raise ValueError(
                f"Invalid notification event: {event}"
            )

    @staticmethod
    def _validate_channels(
        email_enabled,
        line_enabled,
    ):

        if (
            not email_enabled
            and not line_enabled
        ):

            raise ValueError(
                "At least one notification "
                "channel must be enabled."
            )

    # ==========================================
    # Create Bulk
    # ==========================================

    def create_bulk(
        self,
        module,
        event,
        department_id,
        recipients,
        created_by=None,
    ):
        """
        Create multiple notification rules
        in a single transaction.

        recipients format:

        [
            {
                "employee_id": 1,
                "email_enabled": True,
                "line_enabled": False,
            },
            {
                "employee_id": 2,
                "email_enabled": True,
                "line_enabled": True,
            },
        ]
        """

        try:

            # ==========================================
            # Validate Module
            # ==========================================

            self._validate_module(
                module
            )

            # ==========================================
            # Validate Event
            # ==========================================

            self._validate_event(
                event
            )

            # ==========================================
            # Validate Recipients
            # ==========================================

            if not recipients:

                return self.failed(
                    "At least one employee must be selected."
                )

            # ==========================================
            # Validate Department
            # ==========================================

            department = (
                self.department_repository.get_by_id(
                    department_id
                )
            )

            if not department:

                return self.failed(
                    "Department not found."
                )

            # ==========================================
            # Prepare Rules
            # ==========================================

            rules = []

            for recipient in recipients:

                employee_id = recipient.get(
                    "employee_id"
                )

                email_enabled = bool(
                    recipient.get(
                        "email_enabled",
                        False,
                    )
                )

                line_enabled = bool(
                    recipient.get(
                        "line_enabled",
                        False,
                    )
                )

                # ==========================================
                # Validate Employee ID
                # ==========================================

                if not employee_id:

                    return self.failed(
                        "Invalid employee selection."
                    )

                # ==========================================
                # Validate Channels
                # ==========================================

                self._validate_channels(
                    email_enabled,
                    line_enabled,
                )

                # ==========================================
                # Get Employee
                # ==========================================

                employee = (
                    self.employee_repository.get_by_id(
                        employee_id
                    )
                )

                if not employee:

                    return self.failed(
                        f"Employee with ID "
                        f"{employee_id} not found."
                    )

                # ==========================================
                # Validate Employee Status
                # ==========================================

                if employee.status != "ACTIVE":

                    return self.failed(
                        f"Employee "
                        f"{employee.full_name} "
                        f"is not active."
                    )

                # ==========================================
                # Validate Employee Department
                # ==========================================

                # if (
                #     employee.department_id
                #     != department_id
                # ):

                #     return self.failed(
                #         f"Employee "
                #         f"{employee.full_name} "
                #         f"does not belong to the "
                #         f"selected department."
                #     )

                # ==========================================
                # Validate Email
                # ==========================================

                if email_enabled:

                    if not employee.email:

                        return self.failed(
                            f"Employee "
                            f"{employee.full_name} "
                            f"does not have an "
                            f"email address."
                        )

                # ==========================================
                # Validate LINE
                # ==========================================

                if line_enabled:

                    if not employee.line_user_id:

                        return self.failed(
                            f"Employee "
                            f"{employee.full_name} "
                            f"does not have a "
                            f"LINE User ID."
                        )

                # ==========================================
                # Validate Duplicate
                # ==========================================

                if self.repository.exists_rule(
                    module=module,
                    event=event,
                    department_id=department_id,
                    employee_id=employee_id,
                ):

                    return self.failed(
                        f"Notification rule for "
                        f"{employee.full_name} "
                        f"already exists."
                    )

                # ==========================================
                # Create Rule Entity
                # ==========================================

                rule = NotificationRule(
                    module=module,
                    event=event,
                    department_id=department_id,
                    employee_id=employee_id,
                    email_enabled=email_enabled,
                    line_enabled=line_enabled,
                    created_by=created_by,
                )

                rules.append(rule)

            # ==========================================
            # Save All Rules
            # ==========================================

            with TransactionManager():

                for rule in rules:

                    self.repository.create(
                        rule
                    )

            return self.success(
                (
                    f"{len(rules)} notification "
                    f"rule(s) created successfully."
                ),
                rules,
            )

        except ValueError as ex:

            return self.failed(
                str(ex)
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Sync Notification Rules
    # ==========================================

    def sync(
        self,
        module,
        event,
        department_id,
        recipients,
        updated_by=None,
    ):
        """
        Synchronize notification rules for a specific
        module, event, and department.

        recipients format:

        [
            {
                "employee_id": 1,
                "email_enabled": True,
                "line_enabled": False,
            },
            {
                "employee_id": 2,
                "email_enabled": True,
                "line_enabled": True,
            },
        ]

        Rules that are not included in recipients
        will be permanently deleted.
        """

        try:

            # ==========================================
            # Validate Module
            # ==========================================

            self._validate_module(
                module
            )

            # ==========================================
            # Validate Event
            # ==========================================

            self._validate_event(
                event
            )

            # ==========================================
            # Validate Department
            # ==========================================

            department = (
                self.department_repository.get_by_id(
                    department_id
                )
            )

            if not department:

                return self.failed(
                    "Department not found."
                )

            # ==========================================
            # Existing Rules
            # ==========================================

            existing_rules = (
                self.repository.get_by_event(
                    module=module,
                    event=event,
                    department_id=department_id,
                )
            )

            existing_by_employee = {
                rule.employee_id: rule
                for rule in existing_rules
            }

            # ==========================================
            # Prepare Submitted Employee IDs
            # ==========================================

            submitted_employee_ids = set()

            for recipient in recipients:

                employee_id = recipient.get(
                    "employee_id"
                )

                if not employee_id:

                    return self.failed(
                        "Invalid employee selection."
                    )

                try:

                    employee_id = int(
                        employee_id
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    return self.failed(
                        "Invalid employee selection."
                    )

                if employee_id in submitted_employee_ids:

                    return self.failed(
                        "Duplicate employee selection."
                    )

                submitted_employee_ids.add(
                    employee_id
                )

            # ==========================================
            # Validate All Submitted Recipients
            # BEFORE Transaction
            # ==========================================

            prepared_recipients = []

            for recipient in recipients:

                employee_id = int(
                    recipient.get(
                        "employee_id"
                    )
                )

                email_enabled = bool(
                    recipient.get(
                        "email_enabled",
                        False,
                    )
                )

                line_enabled = bool(
                    recipient.get(
                        "line_enabled",
                        False,
                    )
                )

                # ==========================================
                # Validate Channels
                # ==========================================

                self._validate_channels(
                    email_enabled,
                    line_enabled,
                )

                # ==========================================
                # Get Employee
                # ==========================================

                employee = (
                    self.employee_repository.get_by_id(
                        employee_id
                    )
                )

                if not employee:

                    return self.failed(
                        f"Employee with ID "
                        f"{employee_id} not found."
                    )

                # ==========================================
                # Validate Employee Status
                # ==========================================

                if employee.status != "ACTIVE":

                    return self.failed(
                        f"Employee "
                        f"{employee.full_name} "
                        f"is not active."
                    )

                # ==========================================
                # Validate Department
                # ==========================================

                if (
                    employee.department_id
                    != department_id
                ):

                    return self.failed(
                        f"Employee "
                        f"{employee.full_name} "
                        f"does not belong to the "
                        f"selected department."
                    )

                # ==========================================
                # Validate Email
                # ==========================================

                if email_enabled:

                    if not employee.email:

                        return self.failed(
                            f"Employee "
                            f"{employee.full_name} "
                            f"does not have an "
                            f"email address."
                        )

                # ==========================================
                # Validate LINE
                # ==========================================

                if line_enabled:

                    if not employee.line_user_id:

                        return self.failed(
                            f"Employee "
                            f"{employee.full_name} "
                            f"does not have a "
                            f"LINE User ID."
                        )

                prepared_recipients.append(
                    {
                        "employee_id": employee_id,
                        "email_enabled": email_enabled,
                        "line_enabled": line_enabled,
                    }
                )

            # ==========================================
            # Synchronize
            # ==========================================

            created_count = 0
            updated_count = 0
            deleted_count = 0

            with TransactionManager():

                # ==========================================
                # CREATE / UPDATE
                # ==========================================

                for recipient in prepared_recipients:

                    employee_id = (
                        recipient[
                            "employee_id"
                        ]
                    )

                    email_enabled = (
                        recipient[
                            "email_enabled"
                        ]
                    )

                    line_enabled = (
                        recipient[
                            "line_enabled"
                        ]
                    )

                    existing_rule = (
                        existing_by_employee.get(
                            employee_id
                        )
                    )

                    # ------------------------------------------
                    # CREATE
                    # ------------------------------------------

                    if not existing_rule:

                        rule = NotificationRule(
                            module=module,
                            event=event,
                            department_id=(
                                department_id
                            ),
                            employee_id=(
                                employee_id
                            ),
                            email_enabled=(
                                email_enabled
                            ),
                            line_enabled=(
                                line_enabled
                            ),
                            created_by=(
                                updated_by
                            ),
                        )

                        self.repository.create(
                            rule
                        )

                        created_count += 1

                    # ------------------------------------------
                    # UPDATE
                    # ------------------------------------------

                    else:

                        if (
                            existing_rule.email_enabled
                            != email_enabled
                            or
                            existing_rule.line_enabled
                            != line_enabled
                        ):

                            existing_rule.email_enabled = (
                                email_enabled
                            )

                            existing_rule.line_enabled = (
                                line_enabled
                            )

                            existing_rule.updated_by = (
                                updated_by
                            )

                            self.repository.update(
                                existing_rule
                            )

                            updated_count += 1

                # ==========================================
                # HARD DELETE
                # ==========================================

                for employee_id, rule in (
                    existing_by_employee.items()
                ):

                    if (
                        employee_id
                        not in submitted_employee_ids
                    ):

                        self.repository.hard_delete(
                            rule
                        )

                        deleted_count += 1

            # ==========================================
            # Result
            # ==========================================

            message = (
                "Notification configuration saved. "
                f"Created: {created_count}, "
                f"Updated: {updated_count}, "
                f"Deleted: {deleted_count}."
            )

            return self.success(
                message,
                {
                    "created": created_count,
                    "updated": updated_count,
                    "deleted": deleted_count,
                },
            )

        except ValueError as ex:

            return self.failed(
                str(ex)
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )