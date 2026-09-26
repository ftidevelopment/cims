from datetime import datetime
from threading import Thread
import os
from app.extensions import db
from app.core.choices.problem import (
    PROBLEM_STATUS,
    ProblemStatus,
)
from app.services.file_service import FileService
from app.core.upload_folder import (
    UploadFolder,
)
from flask import current_app
from app.repositories.problem_repository import ProblemRepository
from app.repositories.problem_pic_repository import ProblemPICRepository
from app.models.problem import Problem
from app.models.problem_pic import ProblemPIC
from app.services.base_export_service import BaseExportService
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager
from app.models.problem_attachment import (ProblemAttachment,)
from app.repositories.problem_attachment_repository import (ProblemAttachmentRepository,)
from app.services.file_service import (FileService,)
from app.core.upload_folder import (UploadFolder,)
from app.services.authorization_service import (
    AuthorizationService,
)
from app.services.notification_service import (
    NotificationService,
)
from app.core.notification_events import (
    NotificationEvent,
)


class ProblemService(BaseService):

    def __init__(self):

        super().__init__()

        self.repository = ProblemRepository()
        self.problem_pic_repository = ProblemPICRepository()
        self.problem_attachment_repository = (ProblemAttachmentRepository())

        self.export_service = BaseExportService(
            self.repository
        )
        self.authorization_service = (
            AuthorizationService()
        )
        self.notification_service = (
            NotificationService()
        )

    # ==========================================
    # Get All
    # ==========================================

    def get_all(

        self,

        keyword=None,

        status=None,

        priority=None,

        department_id=None,

        date_from=None,

        date_to=None,

        created_by=None,

        is_active=True,

        page=1,

        per_page=10,

        sort_by=None,

        sort_order="desc",

    ):

        return self.repository.get_all(

            keyword=keyword,

            status=status,

            priority=priority,

            department_id=department_id,

            date_from=date_from,

            date_to=date_to,

            created_by=created_by,

            is_active=is_active,

            page=page,

            per_page=per_page,

            sort_by=sort_by,

            sort_order=sort_order,

        )
    # ==========================================
    # Get By ID
    # ==========================================

    def get_by_id(self, problem_id):

        return self.repository.get_by_id(
            problem_id
        )

    # ==========================================
    # Get By Problem No
    # ==========================================

    def get_by_problem_no(
        self,
        problem_no,
    ):
        return self.repository.get_by_problem_no(
            problem_no
        )

    # ==========================================
    # Export Config
    # ==========================================

    def get_export_config(self):

        return [

            {
                "header": "Problem No",
                "field": "problem_no",
                "width": 20,
            },

            {
                "header": "Date",
                "field": "problem_date",
                "width": 15,
            },

            {
                "header": "Title",
                "field": "title",
                "width": 40,
            },

            {
                "header": "Department",
                "field": "department.department_name",
                "width": 25,
            },

            {
                "header": "Reporter",
                "field": "reporter.employee_name",
                "width": 25,
            },

            {
                "header": "Monitor",
                "field": "monitor.employee_name",
                "width": 25,
            },

            {
                "header": "Category",
                "field": "problem_category.problem_category_name",
                "width": 25,
            },

            {
                "header": "Priority",
                "field": "priority",
                "width": 15,
            },

            {
                "header": "Status",
                "field": "status",
                "width": 15,
            },

            {
                "header": "Active",
                "field": "is_active",
                "width": 12,
            }

        ]



    # ==========================================
    # Create
    # ==========================================

    def create(
        self,
        form_data,
        files,
        reporter_employee_id,
        created_by,
    ):

        try:

            # ==========================================
            # Validate Create
            # ==========================================

            self._validate_create(
                form_data
            )

            # ==========================================
            # Database Transaction
            # ==========================================

            with TransactionManager():

                problem = Problem()

                # ------------------------------------------
                # Generate Problem Number
                # ------------------------------------------

                problem.problem_no = (
                    self._generate_problem_no()
                )

                # ------------------------------------------
                # Fill Problem Data
                # ------------------------------------------

                self._fill_problem_create(
                    problem,
                    form_data,
                )

                # ------------------------------------------
                # Reporter
                # ------------------------------------------

                problem.reporter_employee_id = (
                    reporter_employee_id
                )

                # ------------------------------------------
                # Status
                # ------------------------------------------

                problem.status = (
                    ProblemStatus.OPEN
                )

                # ------------------------------------------
                # Created By
                # ------------------------------------------

                problem.created_by = (
                    created_by
                )

                # ------------------------------------------
                # Save Problem
                # ------------------------------------------

                self.repository.create(
                    problem
                )

                # ==========================================
                # Generate Problem ID
                # ==========================================

                db.session.flush()

                if not problem.id:

                    raise ValueError(
                        "Failed to generate Problem ID."
                    )

                # ==========================================
                # Save Problem ID
                # ==========================================
                #
                # Save the ID before the transaction
                # is committed.
                #
                # Celery only needs the Problem ID.
                # ==========================================

                problem_id = problem.id

                # ==========================================
                # Save Attachments
                # ==========================================

                self._save_problem_attachments(
                    problem,
                    files.getlist(
                        "attachments"
                    ),
                )

            # ==================================================
            # DATABASE COMMIT SUCCESS
            # ==================================================
            #
            # The Problem and its attachments have now
            # been committed successfully.
            #
            # Notification is sent asynchronously through
            # Celery so the HTTP request does not wait for
            # Email + LINE processing.
            # ==================================================

            try:

                from app.tasks.notification_tasks import (
                    send_problem_created_notification,
                )

                send_problem_created_notification.delay(
                    problem_id
                )

            except Exception as ex:

                # --------------------------------------------------
                # Notification queue failure must NOT make
                # Problem creation fail.
                # --------------------------------------------------

                print(
                    "PROBLEM CREATED "
                    "CELERY NOTIFICATION QUEUE ERROR:",
                    str(ex),
                )

            # ==========================================
            # Return Success Immediately
            # ==========================================

            return self.success(
                "Problem created successfully.",
                problem,
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
    # Validate Create
    # ==========================================

    def _validate_create(
        self,
        form_data,
    ):

        self.validate_required(
            form_data.get("problem_date"),
            "Problem Date",
        )

        self.validate_required(
            form_data.get("department_id"),
            "Department",
        )

        self.validate_required(
            form_data.get("problem_category_id"),
            "Problem Category",
        )

        self.validate_required(
            form_data.get("title"),
            "Title",
        )

        self.validate_required(
            form_data.get("description"),
            "Description",
        )

        # ==========================================
    # Fill Problem
    # ==========================================

    def _fill_problem_data(
        self,
        problem,
        form_data,
    ):

        problem.problem_date = form_data.get(
            "problem_date"
        )

        problem.department_id = form_data.get(
            "department_id"
        )

        reporter_employee_id = form_data.get(
            "reporter_employee_id"
        )

        if reporter_employee_id:
            problem.reporter_employee_id = (
                reporter_employee_id
            )

        monitor_employee_id = form_data.get(
            "monitor_employee_id"
        )

        if monitor_employee_id:
            problem.monitor_employee_id = (
                monitor_employee_id
            )

        problem.problem_category_id = (
            form_data.get(
                "problem_category_id"
            )
        )

        priority = form_data.get(
            "priority"
        )

        if priority:
            problem.priority = priority

        problem.problem_source = (
            form_data.get(
                "problem_source"
            )
        )

        problem.problem_location = (
            form_data.get(
                "problem_location"
            )
        )

        problem.title = (
            form_data.get("title")
        )

        problem.description = (
            form_data.get("description")
        )

        problem.problem_cause = (
            form_data.get("problem_cause")
        )

        problem.problem_impact = (
            form_data.get("problem_impact")
        )

        problem.loss_quantity = (
            form_data.get("loss_quantity") or 0
        )

        problem.loss_cost = (
            form_data.get("loss_cost") or 0
        )

        problem.loss_time = (
            form_data.get("loss_time") or 0
        )

        problem.attachment = (
            form_data.get("attachment")
        )

        # ==========================================
        # DO NOT UPDATE STATUS HERE
        # ==========================================

        problem.target_date = (
            form_data.get("target_date")
        )

        problem.closed_date = (
            form_data.get("closed_date")
        )
    # ==========================================
    # Fill Problem
    # ==========================================

    def _fill_problem_create(
        self,
        problem,
        form_data,
    ):

        problem.problem_date = form_data.get(
            "problem_date"
        )

        problem.department_id = form_data.get(
            "department_id"
        )

        problem.problem_category_id = form_data.get(
            "problem_category_id"
        )

        problem.problem_source = form_data.get(
            "problem_source"
        )

        problem.problem_location = form_data.get(
            "problem_location"
        )

        problem.title = form_data.get(
            "title"
        )

        problem.description = form_data.get(
            "description"
        )

        problem.problem_cause = form_data.get(
            "problem_cause"
        )

        problem.problem_impact = form_data.get(
            "problem_impact"
        )

        problem.loss_quantity = (
            form_data.get("loss_quantity") or 0
        )

        problem.loss_cost = (
            form_data.get("loss_cost") or 0
        )

        problem.loss_time = (
            form_data.get("loss_time") or 0
        )

        problem.attachment = form_data.get(
            "attachment"
        )

        # ==========================================
    # Generate Problem Number
    # ==========================================

    def _generate_problem_no(self):

        today = datetime.now()

        prefix = today.strftime("P%y%m")

        last_problem = self.repository.get_last_problem_no(
            prefix
        )

        if last_problem:

            last_number = int(
                last_problem.problem_no[-4:]
            )

            running_no = last_number + 1

        else:

            running_no = 1

        return (
            f"{prefix}"
            f"{running_no:04d}"
        )

        # ==========================================
    # Save Problem PIC
    # ==========================================

    def _save_problem_pics(
        self,
        problem_id,
        problem_pics,
    ):

        if not problem_pics:
            return

        for index, employee_id in enumerate(problem_pics):

            problem_pic = ProblemPIC()

            problem_pic.problem_id = problem_id

            problem_pic.employee_id = employee_id

            problem_pic.is_leader = (
                index == 0
            )

            self.problem_pic_repository.create(
                problem_pic
            )

    # ==========================================
    # Update
    # ==========================================


    def update(
        self,
        problem_id,
        form_data,
        files,
        updated_by=None,
        current_employee_id=None,
        current_role_code=None,
    ):

        try:

            # ==========================================
            # Get Problem
            # ==========================================

            problem = self.repository.get_by_id(
                problem_id
            )

            self.validate_exists(
                problem,
                "Problem",
            )

            # ==========================================
            # Authorization
            # ==========================================

            if not self.authorization_service.can_edit_problem(
                problem=problem,
                employee_id=current_employee_id,
                role_code=current_role_code,
            ):

                return self.failed(
                    "You are not authorized to edit this Problem."
                )

            # ==========================================
            # Transaction
            # ==========================================

            with TransactionManager():

                self._fill_problem_data(
                    problem,
                    form_data,
                )

                problem.updated_by = updated_by

                self.repository.update(
                    problem
                )

                # ==========================================
                # Update PIC
                # ==========================================

                self.problem_pic_repository.delete_by(
                    problem_id=problem.id
                )

                self._save_problem_pics(
                    problem.id,
                    form_data.get(
                        "problem_pics",
                        [],
                    ),
                )

                # ==========================================
                # Save Attachments
                # ==========================================

                self._save_problem_attachments(
                    problem,
                    files.getlist(
                        "attachments"
                    ),
                )

           # ==================================================
            # QUEUE NOTIFICATION TO CELERY
            # ==================================================

            try:

                from app.tasks.notification_tasks import (
                    send_problem_updated_notification,
                )

                print(
                    "=========================================="
                )

                print(
                    "QUEUE PROBLEM UPDATED NOTIFICATION"
                )

                print(
                    "Problem ID:",
                    problem.id
                )

                task = send_problem_updated_notification.delay(
                    problem.id
                )

                print(
                    "CELERY TASK ID:",
                    task.id
                )

                print(
                    "PROBLEM UPDATED NOTIFICATION "
                    "SUCCESSFULLY QUEUED"
                )

                print(
                    "=========================================="
                )

            except Exception as ex:

                # --------------------------------------------------
                # Notification queue failure must NOT make
                # Problem update fail.
                # --------------------------------------------------

                print(
                    "=========================================="
                )

                print(
                    "PROBLEM UPDATED "
                    "CELERY NOTIFICATION QUEUE ERROR:",
                    str(ex)
                )

                print(
                    "=========================================="
                )

            # ==========================================
            # Return
            # ==========================================

            return self.success(
                "Problem updated successfully.",
                problem,
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
        problem_id,
        deleted_by=None,
        current_employee_id=None,
        current_role_code=None,
    ):

        try:

            # ==========================================
            # Get Problem
            # ==========================================

            problem = self.repository.get_by_id(
                problem_id
            )

            self.validate_exists(
                problem,
                "Problem",
            )

            # ==========================================
            # Authorization
            # ==========================================

            if not AuthorizationService.can_delete_problem(
                problem=problem,
                employee_id=current_employee_id,
                role_code=current_role_code,
            ):

                return self.failed(
                    "You are not authorized to delete this Problem."
                )

            # ==========================================
            # Transaction
            # ==========================================

            with TransactionManager():

                problem.updated_by = deleted_by

                self.repository.delete(
                    problem
                )

            return self.success(
                "Problem deleted successfully."
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
    # Restore
    # ==========================================

    def restore(
        self,
        problem_id,
    ):

        try:

            problem = self.repository.get_by_id(
                problem_id,
                is_active=False,
            )

            self.validate_exists(
                problem,
                "Problem",
            )

            self.repository.restore(
                problem
            )

            return self.success(
                "Problem restored successfully."
            )

        except ValueError as ex:

            return self.failed(
                str(ex)
            )

        except Exception as ex:

            return self.handle_exception(ex)

    # ==========================================
    # Export Excel
    # ==========================================

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):

        return self.export_service.export(

            sheet_name="Problem",

            export_config=self.get_export_config(),

            keyword=keyword,

            is_active=is_active,

            sort_by=sort_by,

            sort_order=sort_order,
        )

        # ==========================================
    # Create Problem
    # ==========================================

    def _create_problem(
        self,
        problem,
        form_data,
        created_by,
    ):

        problem.problem_no = (
            self._generate_problem_no()
        )

        self._fill_problem_data(
            problem,
            form_data,
        )

        problem.created_by = created_by

        self.repository.create(
            problem
        )

    # ==========================================
    # Save Problem Attachments
    # ==========================================

    def _save_problem_attachments(
        self,
        problem,
        files,
    ):

        if not files:
            return

        sort_order = 1

        for file in files:

            if not file or not file.filename:
                continue

            stored_name = FileService.save(
                file=file,
                folder=UploadFolder.PROBLEM,
            )

            attachment = ProblemAttachment()

            attachment.problem_id = problem.id

            attachment.stored_name = stored_name

            attachment.original_name = (
                file.filename
            )

            attachment.extension = (
                os.path.splitext(
                    file.filename
                )[1]
                .replace(".", "")
                .lower()
            )

            attachment.mime_type = (
                file.content_type
            )

            attachment.file_size = (
                file.content_length or 0
            )

            attachment.is_image = (
                attachment.extension in (
                    "jpg",
                    "jpeg",
                    "png",
                    "gif",
                    "bmp",
                    "webp",
                )
            )

            attachment.sort_order = (
                sort_order
            )

            self.problem_attachment_repository.create(
                attachment
            )

            sort_order += 1

    # ==========================================
    # Background Notification
    # ==========================================

    def _send_problem_created_notification_background(
        self,
        problem_id,
        app,
    ):
        """
        Send Problem Created notification in a
        background thread.

        This method is currently used for
        performance testing so that the HTTP
        response does not wait for Email/LINE.
        """

        try:

            # ==========================================
            # Create Flask Application Context
            # ==========================================

            with app.app_context():

                # ==========================================
                # Reload Problem from Database
                # ==========================================
                #
                # Do not use the original SQLAlchemy object
                # from the request thread.
                #
                # Reload it inside the background thread.
                # ==========================================

                problem = self.repository.get_by_id(
                    problem_id
                )

                if not problem:

                    print(
                        "PROBLEM CREATED "
                        "BACKGROUND NOTIFICATION: "
                        "Problem not found:",
                        problem_id,
                    )

                    return

                # ==========================================
                # Send Notification
                # ==========================================

                self.notification_service.problem_created(
                    problem=problem,
                )

                print(
                    "PROBLEM CREATED "
                    "BACKGROUND NOTIFICATION: "
                    "SUCCESS -",
                    problem.problem_no,
                )

        except Exception as ex:

            print(
                "PROBLEM CREATED "
                "BACKGROUND NOTIFICATION ERROR:",
                str(ex),
            )