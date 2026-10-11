from datetime import datetime

from flask import render_template

from app.core.transaction_manager import (
    TransactionManager,
)

from app.models.notification_log import (
    NotificationLog,
)

from app.models.employee import (
    Employee,
)

from app.repositories.notification_repository import (
    NotificationRepository,
)

from app.repositories.notification_rule_repository import (
    NotificationRuleRepository,
)

from app.services.email_service import (
    EmailService,
)

from app.services.line_service import (
    LineService,
)

from app.core.notification_events import (
    NotificationEvent,
)


# =========================================================
# NOTIFICATION LOG
# =========================================================
#
# False = NotificationLog tidak disimpan ke database.
#
# True = NotificationLog disimpan ke database.
#
# Production setting:
# NotificationLog AKTIF.
# =========================================================

SAVE_NOTIFICATION_LOG = True


class NotificationService:
    """
    Generic service for handling CIMS notifications.
    """

    def __init__(self):

        self.notification_repository = (
            NotificationRepository()
        )

        self.notification_rule_repository = (
            NotificationRuleRepository()
        )

    # ==================================================
    # EMAIL TEMPLATE
    # ==================================================

    def render_email_template(
        self,
        template,
        **context,
    ):

        return render_template(
            template,
            **context,
        )

    # ==================================================
    # LINE TEMPLATE
    # ==================================================

    def render_line_template(
        self,
        module,
        event,
        **context,
    ):
        """
        Render LINE notification template based on
        module and event.

        Example:

        PROBLEM + CREATED
        -> line/problem/created.txt

        PROBLEM + UPDATED
        -> line/problem/updated.txt
        """

        module_folder = module.lower()
        event_file = event.lower()

        template = (
            f"line/"
            f"{module_folder}/"
            f"{event_file}.txt"
        )

        return render_template(
            template,
            **context,
        )

    # ==================================================
    # SAVE NOTIFICATION LOG
    # ==================================================

    def _save_log(
        self,
        event,
        channel,
        recipient,
        subject,
        status,
        error_message=None,
    ):
        """
        Save notification log to database.

        This method is controlled by
        SAVE_NOTIFICATION_LOG.

        If SAVE_NOTIFICATION_LOG = False,
        no database operation is performed.
        """

        # ==============================================
        # Skip database logging
        # ==============================================

        if not SAVE_NOTIFICATION_LOG:

            return None

        # ==============================================
        # Create notification log
        # ==============================================

        notification_log = NotificationLog(
            event=event,
            channel=channel,
            recipient=recipient,
            subject=subject,
            status=status,
            error_message=error_message,
            sent_at=(
                datetime.utcnow()
                if status == "SENT"
                else None
            ),
        )

        # ==============================================
        # Save to database
        # ==============================================

        with TransactionManager():

            self.notification_repository.create(
                notification_log
            )

        return notification_log

    # ==================================================
    # GENERIC NOTIFICATION
    # ==================================================

    def notify(
        self,
        module,
        event,
        department_id,
        subject,
        body,
        html=False,
        additional_employees=None,
        additional_email_employees=None,
        line_context=None,
    ):
        """
        Send notification through configured channels.

        Notification Rules:
            - Determine recipients
            - Determine Email enabled
            - Determine LINE enabled

        Additional Employees:
            - Automatically receive Email + LINE

        Email:
            - Uses send_bulk_email()
            - One SMTP connection for all recipients

        LINE:
            - Uses send_multicast()
            - Maximum 500 LINE User IDs per request

        Notification Log:
            - Controlled by SAVE_NOTIFICATION_LOG

        Recipient rules and business logic are preserved.
        """

        # ==================================================
        # VALIDATE MODULE
        # ==================================================

        if not NotificationEvent.is_valid_module(
            module
        ):

            raise ValueError(
                f"Invalid notification module: {module}"
            )

        # ==================================================
        # VALIDATE EVENT
        # ==================================================

        if not NotificationEvent.is_valid_event(
            module,
            event,
        ):

            raise ValueError(
                f"Invalid notification event: "
                f"{event} for module {module}"
            )

        # ==================================================
        # GET NOTIFICATION RULES
        # ==================================================

        rules = (
            self.notification_rule_repository
            .get_by_event(
                module=module,
                event=event,
                department_id=department_id,
            )
        )

        # ==================================================
        # BUILD UNIQUE RECIPIENTS
        # ==================================================
        #
        # One employee can appear in multiple rules.
        #
        # We merge them by employee ID.
        #
        # Example:
        #
        # Employee A
        # Rule 1 -> Email
        # Rule 2 -> LINE
        #
        # Result:
        # Employee A -> Email + LINE
        #
        # ==================================================

        unique_recipients = {}

        for rule in rules:

            employee = rule.employee

            if not employee:
                continue

            employee_id = employee.id

            if employee_id not in unique_recipients:

                unique_recipients[
                    employee_id
                ] = {

                    "employee": employee,

                    "email_enabled": bool(
                        rule.email_enabled
                    ),

                    "line_enabled": bool(
                        rule.line_enabled
                    ),
                }

            else:

                existing = (
                    unique_recipients[
                        employee_id
                    ]
                )

                existing[
                    "email_enabled"
                ] = (
                    existing[
                        "email_enabled"
                    ]
                    or bool(
                        rule.email_enabled
                    )
                )

                existing[
                    "line_enabled"
                ] = (
                    existing[
                        "line_enabled"
                    ]
                    or bool(
                        rule.line_enabled
                    )
                )

        # ==================================================
        # ADDITIONAL EMPLOYEES
        # ==================================================
        #
        # Additional employees always receive
        # both Email and LINE.
        #
        # This preserves existing behavior.
        #
        # ==================================================

        if additional_employees:

            for employee in additional_employees:

                if not employee:
                    continue

                employee_id = employee.id

                if (
                    employee_id
                    in unique_recipients
                ):

                    existing = (
                        unique_recipients[
                            employee_id
                        ]
                    )

                    existing[
                        "email_enabled"
                    ] = True

                    existing[
                        "line_enabled"
                    ] = True

                else:

                    unique_recipients[
                        employee_id
                    ] = {

                        "employee": employee,

                        "email_enabled": True,

                        "line_enabled": True,
                    }

        # ==================================================
        # ADDITIONAL EMAIL EMPLOYEES
        # ==================================================
        #
        # These employees receive EMAIL only.
        #
        # This is useful for dynamic recipients such as:
        # - Issue Requestor
        # - Developer who requested clarification
        #
        # They do NOT automatically receive LINE.
        # ==================================================

        if additional_email_employees:

            for employee in additional_email_employees:

                if not employee:
                    continue

                employee_id = employee.id

                if employee_id in unique_recipients:

                    existing = unique_recipients[
                        employee_id
                    ]

                    existing["email_enabled"] = True

                else:

                    unique_recipients[
                        employee_id
                    ] = {

                        "employee": employee,

                        "email_enabled": True,

                        "line_enabled": False,
                    }

        # ==================================================
        # NO RECIPIENT
        # ==================================================

        if not unique_recipients:

            return False

        # ==================================================
        # PREPARE EMAIL RECIPIENTS
        # ==================================================

        email_recipients = []

        for recipient in (
            unique_recipients.values()
        ):

            employee = recipient[
                "employee"
            ]

            if not recipient[
                "email_enabled"
            ]:

                continue

            if not employee.email:

                continue

            email = employee.email.strip()

            if not email:

                continue

            email_recipients.append(
                email
            )

        # ==================================================
        # REMOVE DUPLICATE EMAIL
        # ==================================================

        email_recipients = list(
            dict.fromkeys(
                email_recipients
            )
        )

        # ==================================================
        # PREPARE LINE RECIPIENTS
        # ==================================================

        line_recipients = []

        for recipient in (
            unique_recipients.values()
        ):

            employee = recipient[
                "employee"
            ]

            if not recipient[
                "line_enabled"
            ]:

                continue

            if not employee.line_user_id:

                continue

            line_user_id = (
                employee.line_user_id.strip()
            )

            if not line_user_id:

                continue

            line_recipients.append(
                line_user_id
            )

        # ==================================================
        # REMOVE DUPLICATE LINE USER ID
        # ==================================================

        line_recipients = list(
            dict.fromkeys(
                line_recipients
            )
        )

        # ==================================================
        # RENDER LINE TEMPLATE
        # ==================================================
        #
        # LINE message is rendered ONCE.
        #
        # ==================================================

        line_message = None

        line_template_error = None

        if line_recipients:

            if line_context is not None:

                try:

                    line_message = (
                        self.render_line_template(
                            module=module,
                            event=event,
                            **line_context,
                        )
                    )

                    line_message = (
                        line_message.strip()
                    )

                except Exception as ex:

                    line_message = None

                    line_template_error = (
                        str(ex)
                    )

            else:

                line_template_error = (
                    "LINE template context "
                    "was not provided."
                )

        # ==================================================
        # NOTIFICATION STATUS
        # ==================================================

        notification_sent = False

        # ==================================================
        # SEND BULK EMAIL
        # ==================================================

        if email_recipients:

            try:

                EmailService.send_bulk_email(
                    recipients=email_recipients,
                    subject=subject,
                    body=body,
                    html=html,
                )

                # ------------------------------------------
                # Bulk email successful
                # ------------------------------------------

                notification_sent = True

                # ------------------------------------------
                # Save log
                #
                # Controlled by SAVE_NOTIFICATION_LOG
                # ------------------------------------------

                if SAVE_NOTIFICATION_LOG:

                    for recipient in (
                        email_recipients
                    ):

                        self._save_log(
                            event=event,
                            channel="EMAIL",
                            recipient=recipient,
                            subject=subject,
                            status="SENT",
                        )

            except Exception as ex:

                error_message = str(ex)

                # ------------------------------------------
                # Bulk email failed
                # ------------------------------------------

                if SAVE_NOTIFICATION_LOG:

                    for recipient in (
                        email_recipients
                    ):

                        self._save_log(
                            event=event,
                            channel="EMAIL",
                            recipient=recipient,
                            subject=subject,
                            status="FAILED",
                            error_message=error_message,
                        )

        # ==================================================
        # SEND MULTICAST LINE
        # ==================================================

        if line_recipients:

            # ----------------------------------------------
            # LINE template failed
            # ----------------------------------------------

            if not line_message:

                error_message = (
                    line_template_error
                    or
                    "LINE message is empty."
                )

                if SAVE_NOTIFICATION_LOG:

                    for line_user_id in (
                        line_recipients
                    ):

                        self._save_log(
                            event=event,
                            channel="LINE",
                            recipient=line_user_id,
                            subject=subject,
                            status="FAILED",
                            error_message=error_message,
                        )

            # ----------------------------------------------
            # LINE template OK
            # ----------------------------------------------

            else:

                try:

                    LineService.send_multicast(
                        line_user_ids=line_recipients,
                        message=line_message,
                    )

                    # --------------------------------------
                    # Multicast successful
                    # --------------------------------------

                    notification_sent = True

                    # --------------------------------------
                    # Save log
                    #
                    # Controlled by SAVE_NOTIFICATION_LOG
                    # --------------------------------------

                    if SAVE_NOTIFICATION_LOG:

                        for line_user_id in (
                            line_recipients
                        ):

                            self._save_log(
                                event=event,
                                channel="LINE",
                                recipient=line_user_id,
                                subject=subject,
                                status="SENT",
                            )

                except Exception as ex:

                    error_message = str(ex)

                    # --------------------------------------
                    # Multicast failed
                    # --------------------------------------

                    if SAVE_NOTIFICATION_LOG:

                        for line_user_id in (
                            line_recipients
                        ):

                            self._save_log(
                                event=event,
                                channel="LINE",
                                recipient=line_user_id,
                                subject=subject,
                                status="FAILED",
                                error_message=error_message,
                            )

        # ==================================================
        # RETURN
        # ==================================================

        return notification_sent

    # ==================================================
    # PROBLEM CREATED
    # ==================================================

    def problem_created(
        self,
        problem,
    ):

        subject = (
            f"[CIMS] New Problem Created - "
            f"{problem.problem_no}"
        )

        # ----------------------------------------------
        # Existing EMAIL template
        # ----------------------------------------------

        body = (
            self.render_email_template(
                "emails/problem/created.html",
                problem=problem,
                cims_url="http://localhost:5000",
            )
        )

        # ----------------------------------------------
        # EMAIL + LINE
        # ----------------------------------------------

        return self.notify(
            module=NotificationEvent.PROBLEM,
            event=(
                NotificationEvent.PROBLEM_CREATED
            ),
            department_id=problem.department_id,
            subject=subject,
            body=body,
            html=True,

            # Context for:
            # line/problem/created.txt
            line_context={
                "problem": problem,
            },
        )

    # ==================================================
    # PROBLEM UPDATED
    # ==================================================

    def problem_updated(
        self,
        problem,
    ):

        subject = (
            f"[CIMS] Problem Updated - "
            f"{problem.problem_no}"
        )

        # ----------------------------------------------
        # Existing EMAIL template
        # ----------------------------------------------

        body = (
            self.render_email_template(
                "emails/problem/updated.html",
                problem=problem,
                cims_url="http://localhost:5000",
            )
        )

        # ----------------------------------------------
        # EMAIL + LINE
        # ----------------------------------------------

        return self.notify(
            module=NotificationEvent.PROBLEM,
            event=(
                NotificationEvent.PROBLEM_UPDATED
            ),
            department_id=problem.department_id,
            subject=subject,
            body=body,
            html=True,

            # Context for:
            # line/problem/updated.txt
            line_context={
                "problem": problem,
            },
        )


    # ==================================================
    # ISSUE CLARIFICATION REQUESTED
    # ==================================================

    def issue_clarification_requested(
        self,
        clarification,
    ):
        """
        Notify Issue Requestor that additional
        clarification is required.

        Email only for the dynamic requestor.
        """

        issue = clarification.issue

        if not issue:
            return False

        requestor = issue.requestor

        if not requestor:
            return False

        if not requestor.email:
            return False

        subject = (
            f"[CIMS] Clarification Required - "
            f"{issue.issue_no}"
        )

        body = self.render_email_template(
            "emails/issue/clarification_requested.html",
            issue=issue,
            clarification=clarification,
            requestor=requestor,
            cims_url="http://localhost:5000",
        )

        return self.notify(
            module=NotificationEvent.ISSUE,
            event=(
                NotificationEvent
                .ISSUE_CLARIFICATION_REQUESTED
            ),
            department_id=None,
            subject=subject,
            body=body,
            html=True,
            additional_email_employees=[
                requestor,
            ],
        )


    # ==================================================
    # ISSUE CLARIFICATION RESPONDED
    # ==================================================

    def issue_clarification_responded(
        self,
        clarification,
    ):
        """
        Notify the employee who requested the
        clarification that the requestor has responded.

        Email only.
        """

        issue = clarification.issue

        if not issue:
            return False

        requested_by = (
            clarification.requested_by
        )

        if not requested_by:
            return False

        if not requested_by.email:
            return False

        subject = (
            f"[CIMS] Clarification Response - "
            f"{issue.issue_no}"
        )

        body = self.render_email_template(
            "emails/issue/clarification_responded.html",
            issue=issue,
            clarification=clarification,
            requested_by=requested_by,
            cims_url="http://localhost:5000",
        )

        return self.notify(
            module=NotificationEvent.ISSUE,
            event=(
                NotificationEvent
                .ISSUE_CLARIFICATION_RESPONDED
            ),
            department_id=None,
            subject=subject,
            body=body,
            html=True,
            additional_email_employees=[
                requested_by,
            ],
        )

    # ==================================================
    # NOTIFY ALL EMPLOYEES
    # ==================================================

    def notify_all_employees(
        self,
        event,
        subject,
        body,
        html=False,
        line_context=None,
    ):
        """
        Send broadcast notification to all active employees.

        Email:
            Uses send_bulk_email().

        LINE:
            Uses send_multicast().

        Notification Rules are intentionally NOT used.

        Notification Log:
            Controlled by SAVE_NOTIFICATION_LOG.

        Intended for broadcast events such as:

            KAIZEN_AWARDED
        """

        # ----------------------------------------------
        # Validate event
        # ----------------------------------------------

        if not event:

            raise ValueError(
                "Notification event is required."
            )

        # ----------------------------------------------
        # Get all active employees
        # ----------------------------------------------

        employees = (
            Employee.query
            .filter(
                Employee.status == "ACTIVE"
            )
            .all()
        )

        if not employees:

            return False

        # ==================================================
        # PREPARE EMAIL RECIPIENTS
        # ==================================================

        email_recipients = []

        for employee in employees:

            if not employee.email:
                continue

            email = employee.email.strip()

            if not email:
                continue

            if email not in email_recipients:

                email_recipients.append(
                    email
                )

        # ==================================================
        # PREPARE LINE RECIPIENTS
        # ==================================================

        line_recipients = []

        for employee in employees:

            if not employee.line_user_id:
                continue

            line_user_id = (
                employee.line_user_id.strip()
            )

            if not line_user_id:
                continue

            if line_user_id not in line_recipients:

                line_recipients.append(
                    line_user_id
                )

        # ==================================================
        # RENDER LINE TEMPLATE
        # ==================================================

        line_message = None

        line_template_error = None

        if line_context is not None:

            try:

                line_message = (
                    self.render_line_template(
                        module=NotificationEvent.KAIZEN,
                        event=event,
                        **line_context,
                    )
                )

                line_message = (
                    line_message.strip()
                )

            except Exception as ex:

                line_message = None

                line_template_error = str(ex)

        else:

            line_template_error = (
                "LINE template context "
                "was not provided."
            )

        # ==================================================
        # NOTIFICATION STATUS
        # ==================================================

        notification_sent = False

        # ==================================================
        # SEND BULK EMAIL
        # ==================================================

        if email_recipients:

            try:

                EmailService.send_bulk_email(
                    recipients=email_recipients,
                    subject=subject,
                    body=body,
                    html=html,
                )

                notification_sent = True

                # ------------------------------------------
                # Save Email Log
                # ------------------------------------------

                if SAVE_NOTIFICATION_LOG:

                    for recipient in email_recipients:

                        self._save_log(
                            event=event,
                            channel="EMAIL",
                            recipient=recipient,
                            subject=subject,
                            status="SENT",
                        )

            except Exception as ex:

                # ------------------------------------------
                # Bulk Email failed
                # ------------------------------------------

                if SAVE_NOTIFICATION_LOG:

                    for recipient in email_recipients:

                        self._save_log(
                            event=event,
                            channel="EMAIL",
                            recipient=recipient,
                            subject=subject,
                            status="FAILED",
                            error_message=str(ex),
                        )

        # ==================================================
        # SEND LINE MULTICAST
        # ==================================================

        if line_recipients:

            # ----------------------------------------------
            # LINE template error
            # ----------------------------------------------

            if not line_message:

                if SAVE_NOTIFICATION_LOG:

                    for recipient in line_recipients:

                        self._save_log(
                            event=event,
                            channel="LINE",
                            recipient=recipient,
                            subject=subject,
                            status="FAILED",
                            error_message=(
                                line_template_error
                                or
                                "LINE message is empty."
                            ),
                        )

            else:

                try:

                    LineService.send_multicast(
                        line_user_ids=line_recipients,
                        message=line_message,
                    )

                    notification_sent = True

                    # --------------------------------------
                    # Save LINE Log
                    # --------------------------------------

                    if SAVE_NOTIFICATION_LOG:

                        for recipient in line_recipients:

                            self._save_log(
                                event=event,
                                channel="LINE",
                                recipient=recipient,
                                subject=subject,
                                status="SENT",
                            )

                except Exception as ex:

                    # --------------------------------------
                    # Multicast failed
                    # --------------------------------------

                    if SAVE_NOTIFICATION_LOG:

                        for recipient in line_recipients:

                            self._save_log(
                                event=event,
                                channel="LINE",
                                recipient=recipient,
                                subject=subject,
                                status="FAILED",
                                error_message=str(ex),
                            )

        # ==================================================
        # RETURN
        # ==================================================

        return notification_sent

    # ==================================================
    # AUDIT FINDING CREATED
    # ==================================================

    def audit_finding_created(
        self,
        finding,
    ):
        """
        Notify PIC when a new Audit Finding is created.

        The PIC receives:
            - Email
            - LINE

        The PIC is added as an additional employee
        because the PIC is selected dynamically when
        the finding is created.
        """

        # ----------------------------------------------
        # Validate Finding
        # ----------------------------------------------

        if not finding:
            return False

        # ----------------------------------------------
        # Get PIC
        # ----------------------------------------------

        pic = finding.pic_employee

        if not pic:
            return False

        # ----------------------------------------------
        # Subject
        # ----------------------------------------------

        subject = (
            f"[CIMS] New Audit Finding - "
            f"{finding.finding_no}"
        )

        # ----------------------------------------------
        # Email Template
        # ----------------------------------------------

        body = (
            self.render_email_template(
                "emails/audit_finding/created.html",
                finding=finding,
                pic=pic,
                cims_url="http://localhost:5000",
            )
        )

        # ----------------------------------------------
        # Get Audit Department
        # ----------------------------------------------

        department_id = None

        if (
            finding.audit_execution
            and finding.audit_execution.audit_assignment
        ):
            department_id = (
                finding
                .audit_execution
                .audit_assignment
                .department_id
            )


        # ----------------------------------------------
        # Send Email + LINE
        # ----------------------------------------------

        return self.notify(
            module=NotificationEvent.AUDIT_FINDING,
            event=(
                NotificationEvent
                .AUDIT_FINDING_CREATED
            ),
            department_id=department_id,
            subject=subject,
            body=body,
            html=True,

            # PIC receives:
            # Email + LINE
            additional_employees=[
                pic,
            ],

            # Context for:
            # line/audit_finding/created.txt
            line_context={
                "finding": finding,
                "pic": pic,
            },
        )


    # ==================================================
    # AUDIT FINDING SUBMITTED FOR VERIFICATION
    # ==================================================

    def audit_finding_submitted_for_verification(
        self,
        finding,
    ):
        """
        Notify Auditor when an Audit Finding is
        submitted for verification.

        The Auditor receives:
            - Email
            - LINE

        Additional recipients configured through
        Notification Rules will also receive the
        notification according to their channel settings.
        """

        # ----------------------------------------------
        # Validate Finding
        # ----------------------------------------------

        if not finding:
            return False

        # ----------------------------------------------
        # Get Audit Execution
        # ----------------------------------------------

        execution = finding.audit_execution

        if not execution:
            return False

        # ----------------------------------------------
        # Get Audit Assignment
        # ----------------------------------------------

        assignment = execution.audit_assignment

        if not assignment:
            return False

        # ----------------------------------------------
        # Get Auditor
        # ----------------------------------------------

        auditor = assignment.auditor

        if not auditor:
            return False

        # ----------------------------------------------
        # Department
        # ----------------------------------------------

        department_id = assignment.department_id

        # ----------------------------------------------
        # Subject
        # ----------------------------------------------

        subject = (
            f"[CIMS] Audit Finding "
            f"Waiting for Verification - "
            f"{finding.finding_no}"
        )

        # ----------------------------------------------
        # Email Template
        # ----------------------------------------------

        body = (
            self.render_email_template(
                "emails/audit_finding/"
                "submitted_for_verification.html",
                finding=finding,
                auditor=auditor,
                cims_url="http://localhost:5000",
            )
        )

        # ----------------------------------------------
        # Send Email + LINE
        # ----------------------------------------------

        return self.notify(
            module=NotificationEvent.AUDIT_FINDING,

            event=(
                NotificationEvent
                .AUDIT_FINDING_SUBMITTED_FOR_VERIFICATION
            ),

            department_id=department_id,

            subject=subject,

            body=body,

            html=True,

            # Auditor receives:
            # Email + LINE
            additional_employees=[
                auditor,
            ],

            # Context for:
            # line/audit_finding/
            # submitted_for_verification.txt
            line_context={
                "finding": finding,
                "auditor": auditor,
            },
        )

    # ==================================================
    # AUDIT FINDING VERIFIED
    # ==================================================

    def audit_finding_verified(
        self,
        finding,
    ):
        """
        Notify PIC when an Audit Finding
        has been verified by the auditor.

        The PIC receives:
            - Email
            - LINE

        Verification result:
            PASS -> Finding status becomes PASS
            FAIL -> Finding status becomes IN_PROGRESS
        """

        # ----------------------------------------------
        # Validate Finding
        # ----------------------------------------------

        if not finding:
            return False

        # ----------------------------------------------
        # Get PIC
        # ----------------------------------------------

        pic = finding.pic_employee

        if not pic:
            return False

        # ----------------------------------------------
        # Verification Result
        # ----------------------------------------------

        verification_status = (
            finding.verification_status
            or "-"
        )

        # ----------------------------------------------
        # Subject
        # ----------------------------------------------

        if verification_status == "PASS":

            subject = (
                f"[CIMS] Audit Finding Verification "
                f"PASSED - {finding.finding_no}"
            )

        else:

            subject = (
                f"[CIMS] Audit Finding Verification "
                f"FAILED - {finding.finding_no}"
            )

        # ----------------------------------------------
        # Email Template
        # ----------------------------------------------

        body = (
            self.render_email_template(
                "emails/audit_finding/verified.html",
                finding=finding,
                pic=pic,
                cims_url="http://localhost:5000",
            )
        )

        # ----------------------------------------------
        # Send Email + LINE
        # ----------------------------------------------

        return self.notify(
            module=NotificationEvent.AUDIT_FINDING,
            event=(
                NotificationEvent
                .AUDIT_FINDING_VERIFIED
            ),
            department_id=None,
            subject=subject,
            body=body,
            html=True,

            # PIC receives:
            # Email + LINE
            additional_employees=[
                pic,
            ],

            # Context for:
            # line/audit_finding/verified.txt
            line_context={
                "finding": finding,
                "pic": pic,
            },
        )

    # ==================================================
    # AUDIT FINDING OVERDUE
    # ==================================================

    def audit_finding_overdue(
        self,
        finding,
    ):
        """
        Notify PIC and Notification Recipients when
        an Audit Finding becomes overdue.

        Overdue condition:
            target_date < today
            AND
            status != CLOSED

        Recipients:
            - PIC
            - Notification Recipient configured
            for AUDIT_FINDING + OVERDUE

        Channels:
            - PIC -> Email + LINE
            - Notification Recipient -> based on
            Notification Rule settings

        Duplicate protection:
            NotificationLog is checked using
            event + subject.

            If the same overdue notification was
            already sent successfully, notification
            will not be sent again.
        """

        # ==================================================
        # VALIDATE FINDING
        # ==================================================

        if not finding:
            return False

        # ==================================================
        # VALIDATE TARGET DATE
        # ==================================================

        if not finding.target_date:
            return False

        # ==================================================
        # CHECK OVERDUE CONDITION
        # ==================================================

        from datetime import date

        if finding.target_date >= date.today():
            return False

        # ==================================================
        # CLOSED FINDING DOES NOT NEED NOTIFICATION
        # ==================================================

        if finding.status == "CLOSED":
            return False

        # ==================================================
        # SUBJECT
        # ==================================================

        subject = (
            f"[CIMS] Audit Finding Overdue - "
            f"{finding.finding_no}"
        )

        # ==================================================
        # CHECK DUPLICATE NOTIFICATION
        # ==================================================
        #
        # Only a successfully SENT notification counts
        # as already sent.
        #
        # FAILED notification can be retried.
        #
        # ==================================================

        already_sent = (
            self.notification_repository
            .exists_sent_notification_by_subject(
                event=(
                    NotificationEvent
                    .AUDIT_FINDING_OVERDUE
                ),
                subject=subject,
            )
        )

        if already_sent:
            return False

        # ==================================================
        # GET PIC
        # ==================================================

        pic = finding.pic_employee

        if not pic:
            return False

        # ==================================================
        # GET AUDIT EXECUTION
        # ==================================================

        execution = finding.audit_execution

        if not execution:
            return False

        # ==================================================
        # GET AUDIT ASSIGNMENT
        # ==================================================

        assignment = execution.audit_assignment

        if not assignment:
            return False

        # ==================================================
        # GET DEPARTMENT
        # ==================================================

        department_id = assignment.department_id

        # ==================================================
        # EMAIL TEMPLATE
        # ==================================================

        body = self.render_email_template(
            "emails/audit_finding/overdue.html",
            finding=finding,
            pic=pic,
            assignment=assignment,
            execution=execution,
            cims_url="http://localhost:5000",
        )

        # ==================================================
        # SEND EMAIL + LINE
        # ==================================================
        #
        # PIC:
        #   additional_employees
        #   -> Email + LINE
        #
        # Notification Recipient:
        #   notify() gets them from NotificationRule
        #   using:
        #
        #       AUDIT_FINDING
        #       OVERDUE
        #       department_id
        #
        # notify() automatically merges duplicate
        # employees.
        #
        # ==================================================

        return self.notify(
            module=(
                NotificationEvent
                .AUDIT_FINDING
            ),
            event=(
                NotificationEvent
                .AUDIT_FINDING_OVERDUE
            ),
            department_id=department_id,
            subject=subject,
            body=body,
            html=True,

            # ----------------------------------------------
            # PIC always receives Email + LINE
            # ----------------------------------------------

            additional_employees=[
                pic,
            ],

            # ----------------------------------------------
            # LINE context
            # ----------------------------------------------

            line_context={
                "finding": finding,
                "pic": pic,
                "assignment": assignment,
                "execution": execution,
                "cims_url": "http://localhost:5000",
            },
        )