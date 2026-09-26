from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_login import (
    login_required,
    current_user,
)

from app.repositories.department_repository import (
    DepartmentRepository,
)

from app.repositories.employee_repository import (
    EmployeeRepository,
)

from app.services.notification_rule_service import (
    NotificationRuleService,
)

from app.core.notification_events import (
    NotificationEvent,
)


# ==========================================================
# Blueprint
# ==========================================================

notification_rule_bp = Blueprint(
    "notification_rule",
    __name__,
    url_prefix="/notification-rules",
)


# ==========================================================
# Repository / Service
# ==========================================================

notification_rule_service = (
    NotificationRuleService()
)

department_repository = (
    DepartmentRepository()
)

employee_repository = (
    EmployeeRepository()
)


# ==========================================================
# LIST
# ==========================================================

@notification_rule_bp.route("/")
@login_required
def index():

    # ======================================================
    # Pagination
    # ======================================================

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    if page < 1:
        page = 1


    # ======================================================
    # Keyword
    # ======================================================

    keyword = request.args.get(
        "keyword",
        "",
    ).strip()


    # ======================================================
    # Module
    # ======================================================

    module = request.args.get(
        "module",
        "",
    ).strip().upper()


    # ======================================================
    # Event
    # ======================================================

    event = request.args.get(
        "event",
        "",
    ).strip().upper()


    # ======================================================
    # Department
    #
    # IMPORTANT:
    # Department = SOURCE department
    # ======================================================

    department_id = request.args.get(
        "department_id",
        None,
        type=int,
    )


    # ======================================================
    # Master Data
    # ======================================================

    departments = (
        department_repository.get_active()
    )

    modules = (
        NotificationEvent.get_modules()
    )


    # ======================================================
    # Events
    # ======================================================

    if module:

        events = (
            NotificationEvent.get_events(
                module
            )
        )

    else:

        events = []


    # ======================================================
    # Validate Module
    # ======================================================

    if (
        module
        and not NotificationEvent.is_valid_module(
            module
        )
    ):

        module = ""
        event = ""


    # ======================================================
    # Validate Event
    # ======================================================

    if (
        module
        and event
        and not NotificationEvent.is_valid_event(
            module,
            event,
        )
    ):

        event = ""


    # ======================================================
    # Get Notification Rules
    # ======================================================

    pagination = (
        notification_rule_service.get_all(

            keyword=keyword,

            module=module,

            event=event,

            department_id=department_id,

            page=page,

            per_page=10,
        )
    )


    # ======================================================
    # Render
    # ======================================================

    return render_template(

        "notification_rule/list.html",

        pagination=pagination,

        keyword=keyword,

        module=module,

        event=event,

        department_id=department_id,

        modules=modules,

        events=events,

        departments=departments,
    )


# ==========================================================
# CREATE / CONFIGURATION
# ==========================================================

@notification_rule_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
def create():

    # ======================================================
    # Master Data
    # ======================================================

    departments = (
        department_repository.get_active()
    )

    modules = (
        NotificationEvent.get_modules()
    )

    events_by_module = {

        module: NotificationEvent.get_events(
            module
        )

        for module in modules

    }


    # ======================================================
    # Selected Module
    # ======================================================

    selected_module = (
        request.values.get(
            "module",
            "",
        )
        .strip()
        .upper()
    )


    # ======================================================
    # Selected Event
    # ======================================================

    selected_event = (
        request.values.get(
            "event",
            "",
        )
        .strip()
        .upper()
    )


    # ======================================================
    # Selected Department
    #
    # IMPORTANT:
    #
    # This is the SOURCE department.
    #
    # Example:
    #
    # Production
    #     ↓
    # Create Problem
    #     ↓
    # Budi - Purchasing
    #
    # ======================================================

    selected_department_id = (
        request.values.get(
            "department_id",
            type=int,
        )
    )


    # ======================================================
    # NIK Search
    #
    # This is RECIPIENT employee.
    #
    # It is NOT used to determine department.
    # ======================================================

    selected_nik = (
        request.values.get(
            "nik",
            "",
        )
        .strip()
    )


    # ======================================================
    # Events
    # ======================================================

    events = (

        NotificationEvent.get_events(
            selected_module
        )

        if selected_module

        else []

    )


    # ======================================================
    # Employees
    # ======================================================

    employees = []


    # ======================================================
    # Existing Rules
    # ======================================================

    existing_rules = {}


    # ======================================================
    # VALIDATE BASIC FILTER
    # ======================================================

    if selected_module:

        if not NotificationEvent.is_valid_module(
            selected_module
        ):

            flash(
                "Invalid notification module.",
                "danger",
            )

            return redirect(
                url_for(
                    "notification_rule.create"
                )
            )


    if selected_module and selected_event:

        if not NotificationEvent.is_valid_event(
            selected_module,
            selected_event,
        ):

            flash(
                "Invalid event for the selected module.",
                "danger",
            )

            return redirect(
                url_for(
                    "notification_rule.create",
                    module=selected_module,
                )
            )


    # ======================================================
    # LOAD EMPLOYEES
    #
    # Department is ALWAYS required.
    #
    # NIK is only a recipient search.
    # ======================================================

    if (
        selected_module
        and selected_event
        and selected_department_id
    ):

        # --------------------------------------------------
        # Load existing rules for SOURCE department
        # --------------------------------------------------

        rules = (
            notification_rule_service
            .repository
            .get_by_event(

                module=selected_module,

                event=selected_event,

                department_id=(
                    selected_department_id
                ),

            )
        )


        existing_rules = {

            rule.employee_id: rule

            for rule in rules

        }


        # --------------------------------------------------
        # NIK Search
        # --------------------------------------------------

        if selected_nik:

            employee = (
                employee_repository
                .get_active_by_nik(
                    selected_nik
                )
            )

            if employee:

                # ------------------------------------------
                # Only ACTIVE employee can be recipient
                # ------------------------------------------

                if employee.status == "ACTIVE":

                    employees = [
                        employee
                    ]

                else:

                    flash(
                        "The selected employee is not active.",
                        "warning",
                    )

            else:

                flash(
                    f"Employee with NIK "
                    f"'{selected_nik}' "
                    f"was not found.",
                    "warning",
                )


        # --------------------------------------------------
        # No NIK
        #
        # Show all employees from selected SOURCE
        # department.
        # --------------------------------------------------

        else:

            employees = (
                employee_repository
                .get_active_by_department(
                    selected_department_id
                )
            )


    # ======================================================
    # SAVE CONFIGURATION
    # ======================================================

    if request.method == "POST":

        # ==================================================
        # Validate Module
        # ==================================================

        if not selected_module:

            flash(
                "Module is required.",
                "danger",
            )

            return redirect(
                url_for(
                    "notification_rule.create"
                )
            )


        if not NotificationEvent.is_valid_module(
            selected_module
        ):

            flash(
                "Invalid notification module.",
                "danger",
            )

            return redirect(
                url_for(
                    "notification_rule.create"
                )
            )


        # ==================================================
        # Validate Event
        # ==================================================

        if not selected_event:

            flash(
                "Event is required.",
                "danger",
            )

            return redirect(
                url_for(
                    "notification_rule.create",
                    module=selected_module,
                )
            )


        if not NotificationEvent.is_valid_event(
            selected_module,
            selected_event,
        ):

            flash(
                "Invalid event for the selected module.",
                "danger",
            )

            return redirect(
                url_for(
                    "notification_rule.create",
                    module=selected_module,
                )
            )


        # ==================================================
        # Validate SOURCE Department
        # ==================================================

        if not selected_department_id:

            flash(
                "Department is required.",
                "danger",
            )

            return redirect(
                url_for(
                    "notification_rule.create",
                    module=selected_module,
                    event=selected_event,
                )
            )


        # ==================================================
        # Determine Save Mode
        #
        # NIK entered:
        #     update ONLY that employee rule.
        #
        # No NIK:
        #     synchronize SOURCE department employees.
        # ==================================================

        if selected_nik:

            # ==================================================
            # NIK MODE
            # ==================================================

            employee = (
                employee_repository
                .get_by_nik(
                    selected_nik
                )
            )


            # --------------------------------------------------
            # Employee not found
            # --------------------------------------------------

            if not employee:

                flash(
                    f"Employee with NIK "
                    f"'{selected_nik}' "
                    f"was not found.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "notification_rule.create",

                        module=selected_module,

                        event=selected_event,

                        department_id=(
                            selected_department_id
                        ),

                        nik=selected_nik,
                    )
                )


            # --------------------------------------------------
            # Employee must be active
            # --------------------------------------------------

            if employee.status != "ACTIVE":

                flash(
                    "Selected employee is not active.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "notification_rule.create",

                        module=selected_module,

                        event=selected_event,

                        department_id=(
                            selected_department_id
                        ),

                        nik=selected_nik,
                    )
                )


            employee_id = employee.id


            # ==================================================
            # Selected Checkbox
            # ==================================================

            selected_employee_ids = (
                request.form.getlist(
                    "employee_ids"
                )
            )


            is_selected = (
                str(employee_id)
                in selected_employee_ids
            )


            # ==================================================
            # Existing Rule
            # ==================================================

            existing_rule = next(
                (
                    rule
                    for rule in (
                        notification_rule_service
                        .repository
                        .get_by_event(

                            module=selected_module,

                            event=selected_event,

                            department_id=(
                                selected_department_id
                            ),

                        )
                    )

                    if rule.employee_id == employee_id

                ),
                None,
            )


            # ==================================================
            # Employee UNCHECKED
            #
            # Delete only this employee's rule.
            #
            # DO NOT use sync().
            # ==================================================

            if not is_selected:

                if existing_rule:

                    result = (
                        notification_rule_service
                        .delete(
                            rule_id=existing_rule.id,
                            updated_by=(
                                getattr(
                                    current_user,
                                    "username",
                                    None,
                                )
                            ),
                        )
                    )

                    if result.success:

                        flash(
                            result.message,
                            "success",
                        )

                    else:

                        flash(
                            result.message,
                            "danger",
                        )

                else:

                    flash(
                        "No notification rule found for "
                        "the selected employee.",
                        "info",
                    )


            # ==================================================
            # Employee CHECKED
            # ==================================================

            else:

                email_enabled = (
                    request.form.get(
                        f"email_enabled_{employee_id}"
                    )
                    == "1"
                )

                line_enabled = (
                    request.form.get(
                        f"line_enabled_{employee_id}"
                    )
                    == "1"
                )


                # ----------------------------------------------
                # Existing Rule -> UPDATE
                # ----------------------------------------------

                if existing_rule:

                    result = (
                        notification_rule_service
                        .update(

                            rule_id=(
                                existing_rule.id
                            ),

                            email_enabled=(
                                email_enabled
                            ),

                            line_enabled=(
                                line_enabled
                            ),

                            updated_by=(
                                getattr(
                                    current_user,
                                    "username",
                                    None,
                                )
                            ),

                        )
                    )


                # ----------------------------------------------
                # No Rule -> CREATE
                # ----------------------------------------------

                else:

                    result = (
                        notification_rule_service
                        .create(

                            module=selected_module,

                            event=selected_event,

                            department_id=(
                                selected_department_id
                            ),

                            employee_id=employee_id,

                            email_enabled=(
                                email_enabled
                            ),

                            line_enabled=(
                                line_enabled
                            ),

                            created_by=(
                                getattr(
                                    current_user,
                                    "username",
                                    None,
                                )
                            ),

                        )
                    )


                # ----------------------------------------------
                # Result
                # ----------------------------------------------

                if result.success:

                    flash(
                        result.message,
                        "success",
                    )

                else:

                    flash(
                        result.message,
                        "danger",
                    )


            # ==================================================
            # Return to NIK Search
            # ==================================================

            return redirect(
                url_for(

                    "notification_rule.create",

                    module=selected_module,

                    event=selected_event,

                    department_id=(
                        selected_department_id
                    ),

                    nik=selected_nik,

                )
            )


        # ======================================================
        # DEPARTMENT MODE
        #
        # Synchronize all employees belonging to SOURCE
        # department.
        # ======================================================

        employee_ids = (
            request.form.getlist(
                "employee_ids"
            )
        )


        recipients = []


        for employee_id in employee_ids:

            try:

                employee_id = int(
                    employee_id
                )

            except (
                TypeError,
                ValueError,
            ):

                flash(
                    "Invalid employee selection.",
                    "danger",
                )

                return redirect(
                    url_for(

                        "notification_rule.create",

                        module=selected_module,

                        event=selected_event,

                        department_id=(
                            selected_department_id
                        ),

                    )
                )


            email_enabled = (
                request.form.get(
                    f"email_enabled_{employee_id}"
                )
                == "1"
            )


            line_enabled = (
                request.form.get(
                    f"line_enabled_{employee_id}"
                )
                == "1"
            )


            recipients.append(

                {
                    "employee_id": employee_id,

                    "email_enabled": (
                        email_enabled
                    ),

                    "line_enabled": (
                        line_enabled
                    ),
                }

            )


        # ======================================================
        # Synchronize
        #
        # Department mode only.
        #
        # ======================================================

        result = (
            notification_rule_service.sync(

                module=selected_module,

                event=selected_event,

                department_id=(
                    selected_department_id
                ),

                recipients=recipients,

                updated_by=(
                    getattr(
                        current_user,
                        "username",
                        None,
                    )
                ),

            )
        )


        # ======================================================
        # Result Message
        # ======================================================

        if result.success:

            flash(
                result.message,
                "success",
            )

        else:

            flash(
                result.message,
                "danger",
            )


        return redirect(
            url_for(

                "notification_rule.create",

                module=selected_module,

                event=selected_event,

                department_id=(
                    selected_department_id
                ),

            )
        )


    # ======================================================
    # Render
    # ======================================================

    return render_template(

        "notification_rule/create.html",

        departments=departments,

        modules=modules,

        events=events,

        events_by_module=events_by_module,

        employees=employees,

        existing_rules=existing_rules,

        selected_module=selected_module,

        selected_event=selected_event,

        selected_department_id=(
            selected_department_id
        ),

        selected_nik=selected_nik,

    )


# ==========================================================
# DELETE SINGLE RULE
# ==========================================================

@notification_rule_bp.route(
    "/<int:rule_id>/delete",
    methods=["POST"],
)
@login_required
def delete(rule_id):

    result = (
        notification_rule_service.delete(

            rule_id=rule_id,

            updated_by=(
                getattr(
                    current_user,
                    "username",
                    None,
                )
            ),

        )
    )


    if result.success:

        flash(
            result.message,
            "success",
        )

    else:

        flash(
            result.message,
            "danger",
        )


    return redirect(
        url_for(
            "notification_rule.index"
        )
    )