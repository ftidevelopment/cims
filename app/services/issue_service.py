from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.issue import Issue
from app.models.issue_attachment import IssueAttachment
from app.repositories.issue_repository import IssueRepository
from app.repositories.issue_attachment_repository import (
    IssueAttachmentRepository,
)
from app.services.base_service import BaseService

from app.core.choices.issue import (
    ISSUE_MODULES,
    ISSUE_CATEGORIES,
    ISSUE_PRIORITIES,
    ISSUE_STATUS,
)


class IssueService(BaseService):
    """
    Service for Issue Management.

    Workflow:

        OPEN
          ↓
        IN_PROGRESS
          ↓
        FINISH
          ↓
        CLOSE

    If requestor confirms that the issue still exists:

        FINISH
          ↓
        IN_PROGRESS
    """

    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    ALLOWED_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "csv",
        "txt",
        "zip",
    }
    MAX_CREATE_RETRIES = 5
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB per file

    def __init__(self):
        self.repository = IssueRepository()
        self.attachment_repository = IssueAttachmentRepository()

    # ==========================================================
    # CHOICES
    # ==========================================================

    @staticmethod
    def get_modules():
        return ISSUE_MODULES

    @staticmethod
    def get_categories():
        return ISSUE_CATEGORIES

    @staticmethod
    def get_priorities():
        return ISSUE_PRIORITIES

    @staticmethod
    def get_statuses():
        return ISSUE_STATUS

    # ==========================================================
    # CHOICE VALIDATION
    # ==========================================================

    @staticmethod
    def _is_valid_choice(value, choices):
        valid_values = {
            item[0]
            for item in choices
        }

        return value in valid_values

    def _validate_issue_data(
        self,
        module,
        category,
        priority,
        description,
    ):
        """
        Validate Issue creation data.
        """

        result = self.validate(
            self.validate_required(
                module,
                "Module",
            ),
            self.validate_required(
                category,
                "Category",
            ),
            self.validate_required(
                priority,
                "Priority",
            ),
            self.validate_required(
                description,
                "Description",
            ),
        )

        if not result.success:
            return result

        if not self._is_valid_choice(
            module,
            ISSUE_MODULES,
        ):
            return self.failed(
                "Invalid module."
            )

        if not self._is_valid_choice(
            category,
            ISSUE_CATEGORIES,
        ):
            return self.failed(
                "Invalid category."
            )

        if not self._is_valid_choice(
            priority,
            ISSUE_PRIORITIES,
        ):
            return self.failed(
                "Invalid priority."
            )

        return self.success()

    # ==========================================================
    # ISSUE NUMBER
    # ==========================================================

    def _generate_issue_no(self):
        year = datetime.now().year
        prefix = f"ISS-{year}-"

        last_issue = (
            Issue.query
            .filter(
                Issue.issue_no.like(
                    f"{prefix}%"
                )
            )
            .order_by(
                Issue.issue_no.desc()
            )
            .first()
        )

        if not last_issue:
            sequence = 1

        else:
            try:
                last_sequence = int(
                    last_issue.issue_no.split("-")[-1]
                )

                sequence = last_sequence + 1

            except (
                ValueError,
                IndexError,
            ):
                sequence = 1

        return f"{prefix}{sequence:04d}"

    # ==========================================================
    # ATTACHMENT VALIDATION
    # ==========================================================

    @staticmethod
    def _get_file_extension(filename):
        """
        Get lowercase file extension.
        """

        if not filename or "." not in filename:
            return ""

        return filename.rsplit(
            ".",
            1
        )[1].lower()

    def _validate_attachment(self, file):
        """
        Validate uploaded attachment.
        """

        if not file:
            return self.failed(
                "Invalid attachment."
            )

        if not file.filename:
            return self.failed(
                "Attachment file name is required."
            )

        extension = self._get_file_extension(
            file.filename
        )

        if extension not in self.ALLOWED_EXTENSIONS:
            return self.failed(
                f"File type '.{extension}' is not allowed."
            )

        # ------------------------------------------------------
        # File size
        # ------------------------------------------------------

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        if file_size > self.MAX_FILE_SIZE:
            return self.failed(
                "Attachment file size cannot exceed "
                "10 MB."
            )

        return self.success(
            data={
                "extension": extension,
                "file_size": file_size,
            }
        )

    # ==========================================================
    # ATTACHMENT DIRECTORY
    # ==========================================================

    def _get_attachment_directory(self, issue_no):
        """
        Create and return directory for an Issue's attachments.

        Example:

            uploads/issues/ISS-2026-0001/
        """

        upload_folder = current_app.config.get(
            "UPLOAD_FOLDER",
            "uploads",
        )

        attachment_directory = (
            Path(upload_folder)
            / "issues"
            / issue_no
        )

        attachment_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return attachment_directory

    # ==========================================================
    # SAVE ATTACHMENT FILE
    # ==========================================================

    def _save_attachment_file(
        self,
        issue,
        file,
        sort_order,
        description=None,
        created_by=None,
    ):
        """
        Save physical file and create IssueAttachment entity.
        """

        validation = self._validate_attachment(
            file
        )

        if not validation.success:
            raise ValueError(
                validation.message
            )

        extension = validation.data["extension"]
        file_size = validation.data["file_size"]

        original_filename = secure_filename(
            file.filename
        )

        if not original_filename:
            raise ValueError(
                "Invalid attachment file name."
            )

        # ------------------------------------------------------
        # Generate unique stored name
        # ------------------------------------------------------

        stored_name = (
            f"{uuid4().hex}."
            f"{extension}"
        )

        attachment_directory = (
            self._get_attachment_directory(
                issue.issue_no
            )
        )

        file_path = (
            attachment_directory
            / stored_name
        )

        # ------------------------------------------------------
        # Save physical file
        # ------------------------------------------------------

        file.save(
            str(file_path)
        )

        # ------------------------------------------------------
        # Normalize description
        # ------------------------------------------------------

        if description is not None:
            description = description.strip()

        # ------------------------------------------------------
        # Create database record
        # ------------------------------------------------------

        attachment = IssueAttachment(
            issue_id=issue.id,
            file_name=original_filename,
            stored_name=stored_name,
            file_path=str(file_path),
            file_type=extension,
            file_size=file_size,
            description=description or None,
            sort_order=sort_order,
            created_by=created_by,
        )

        self.attachment_repository.create(
            attachment
        )

        return attachment

    # ==========================================================
    # CREATE ISSUE
    # ==========================================================

    def create_issue(
        self,
        module,
        category,
        priority,
        description,
        requestor_employee_id,
        attachments=None,
        attachment_descriptions=None,
        created_by=None,
    ):
        validation = self._validate_issue_data(
            module=module,
            category=category,
            priority=priority,
            description=description,
        )

        if not validation.success:
            return validation

        requestor_result = self.validate_required(
            requestor_employee_id,
            "Requestor",
        )

        if not requestor_result.success:
            return requestor_result

        if attachments is None:
            attachments = []

        if attachment_descriptions is None:
            attachment_descriptions = []

        for attempt in range(self.MAX_CREATE_RETRIES):

            saved_file_paths = []

            try:
                issue_no = self._generate_issue_no()

                issue = Issue(
                    issue_no=issue_no,
                    module=module,
                    category=category,
                    priority=priority,
                    description=description.strip(),
                    status="OPEN",
                    requestor_employee_id=requestor_employee_id,
                    developer_employee_id=None,
                    finished_at=None,
                    closed_at=None,
                    created_by=created_by,
                )

                self.repository.create(issue)

                db.session.flush()

                sort_order = 1

                for index, file in enumerate(attachments):

                    attachment_description = None

                    if index < len(attachment_descriptions):
                        attachment_description = (
                            attachment_descriptions[index]
                        )

                    attachment = self._save_attachment_file(
                        issue=issue,
                        file=file,
                        sort_order=sort_order,
                        description=attachment_description,
                        created_by=created_by,
                    )

                    saved_file_paths.append(
                        Path(attachment.file_path)
                    )

                    sort_order += 1

                db.session.commit()

                return self.success(
                    message=(
                        f"Issue {issue.issue_no} "
                        "created successfully."
                    ),
                    data=issue,
                )

            except Exception as exception:

                db.session.rollback()

                # ----------------------------------------------
                # Cleanup physical files
                # ----------------------------------------------

                for file_path in saved_file_paths:

                    try:

                        if file_path.exists():
                            file_path.unlink()

                    except Exception:
                        pass

                # ----------------------------------------------
                # Retry
                # ----------------------------------------------

                if "Duplicate entry" in str(exception):

                    continue

                return self.failed(
                    "Failed to create Issue: "
                    f"{str(exception)}"
                )

        return self.failed(
            "Failed to generate a unique Issue No. "
            "Please try again."
        )

    # ==========================================================
    # GET ISSUE
    # ==========================================================

    def get_by_id(self, issue_id):
        return self.repository.get_by_id(
            issue_id
        )

    def get_by_issue_no(self, issue_no):
        return self.repository.get_by_issue_no(
            issue_no
        )

    def get_all(
        self,
        keyword=None,
        is_active=True,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="desc",
    ):
        return self.repository.get_all(
            keyword=keyword,
            is_active=is_active,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_active(self):
        return self.repository.get_active()

    # ==========================================================
    # GET ATTACHMENTS
    # ==========================================================

    def get_attachments(self, issue_id):
        """
        Get active attachments for an Issue.
        """

        return (
            self.attachment_repository
            .get_by_issue(issue_id)
        )

    # ==========================================================
    # GET ATTACHMENT
    # ==========================================================

    def get_attachment(self, attachment_id):
        """
        Get active attachment by ID.
        """

        return (
            self.attachment_repository
            .get_by_id(attachment_id)
        )

    # ==========================================================
    # ADD ATTACHMENT
    # ==========================================================

    def add_attachment(
        self,
        issue_id,
        file,
        description=None,
        created_by=None,
    ):
        """
        Add a new attachment to an existing Issue.
        """

        issue = self.repository.get_by_id(
            issue_id
        )

        if not issue:
            return self.failed(
                "Issue not found."
            )

        # ------------------------------------------------------
        # Validate file
        # ------------------------------------------------------

        validation = self._validate_attachment(
            file
        )

        if not validation.success:
            return validation

        try:

            # --------------------------------------------------
            # Get next sort order
            # --------------------------------------------------

            sort_order = (
                self.attachment_repository
                .get_next_sort_order(issue.id)
            )

            # --------------------------------------------------
            # Save attachment
            # --------------------------------------------------

            attachment = self._save_attachment_file(
                issue=issue,
                file=file,
                sort_order=sort_order,
                description=description,
                created_by=created_by,
            )

            db.session.commit()

            return self.success(
                message=(
                    "Attachment uploaded successfully."
                ),
                data=attachment,
            )

        except Exception as exception:

            db.session.rollback()

            return self.failed(
                "Failed to upload attachment: "
                f"{str(exception)}"
            )

    # ==========================================================
    # START ISSUE
    # ==========================================================

    def start_issue(
        self,
        issue_id,
        developer_employee_id,
        updated_by=None,
    ):
        """
        Workflow:

            OPEN → IN_PROGRESS
        """

        issue = self.repository.get_by_id(
            issue_id
        )

        if not issue:
            return self.failed(
                "Issue not found."
            )

        if issue.status != "OPEN":
            return self.failed(
                "Only OPEN issues can be started."
            )

        developer_result = self.validate_required(
            developer_employee_id,
            "Developer",
        )

        if not developer_result.success:
            return developer_result

        issue.developer_employee_id = (
            developer_employee_id
        )

        issue.status = "IN_PROGRESS"
        issue.updated_by = updated_by

        try:

            self.repository.update(
                issue
            )

            db.session.commit()

            return self.success(
                message=(
                    f"Issue {issue.issue_no} "
                    "is now IN PROGRESS."
                ),
                data=issue,
            )

        except Exception as exception:

            db.session.rollback()

            return self.failed(
                "Failed to start Issue: "
                f"{str(exception)}"
            )

    # ==========================================================
    # FINISH ISSUE
    # ==========================================================

    def finish_issue(
        self,
        issue_id,
        updated_by=None,
    ):
        """
        Workflow:

            IN_PROGRESS → FINISH
        """

        issue = self.repository.get_by_id(
            issue_id
        )

        if not issue:
            return self.failed(
                "Issue not found."
            )

        if issue.status != "IN_PROGRESS":
            return self.failed(
                "Only IN_PROGRESS issues "
                "can be finished."
            )

        issue.status = "FINISH"
        issue.finished_at = datetime.now()
        issue.updated_by = updated_by

        try:

            self.repository.update(
                issue
            )

            db.session.commit()

            return self.success(
                message=(
                    f"Issue {issue.issue_no} "
                    "has been finished."
                ),
                data=issue,
            )

        except Exception as exception:

            db.session.rollback()

            return self.failed(
                "Failed to finish Issue: "
                f"{str(exception)}"
            )

    # ==========================================================
    # CLOSE ISSUE
    # ==========================================================

    def close_issue(
        self,
        issue_id,
        updated_by=None,
    ):
        """
        Requestor confirms issue is solved.

        Workflow:

            FINISH → CLOSE
        """

        issue = self.repository.get_by_id(
            issue_id
        )

        if not issue:
            return self.failed(
                "Issue not found."
            )

        if issue.status != "FINISH":
            return self.failed(
                "Only FINISH issues "
                "can be closed."
            )

        issue.status = "CLOSE"
        issue.closed_at = datetime.now()
        issue.updated_by = updated_by

        try:

            self.repository.update(
                issue
            )

            db.session.commit()

            return self.success(
                message=(
                    f"Issue {issue.issue_no} "
                    "has been closed."
                ),
                data=issue,
            )

        except Exception as exception:

            db.session.rollback()

            return self.failed(
                "Failed to close Issue: "
                f"{str(exception)}"
            )

    # ==========================================================
    # ISSUE STILL EXISTS
    # ==========================================================

    def reopen_issue(
        self,
        issue_id,
        updated_by=None,
    ):
        """
        Requestor says the issue still exists.

        Workflow:

            FINISH → IN_PROGRESS
        """

        issue = self.repository.get_by_id(
            issue_id
        )

        if not issue:
            return self.failed(
                "Issue not found."
            )

        if issue.status != "FINISH":
            return self.failed(
                "Only FINISH issues can be "
                "returned to IN PROGRESS."
            )

        issue.status = "IN_PROGRESS"
        issue.finished_at = None
        issue.closed_at = None
        issue.updated_by = updated_by

        try:

            self.repository.update(
                issue
            )

            db.session.commit()

            return self.success(
                message=(
                    f"Issue {issue.issue_no} "
                    "has been returned "
                    "to IN PROGRESS."
                ),
                data=issue,
            )

        except Exception as exception:

            db.session.rollback()

            return self.failed(
                "Failed to return Issue "
                f"to IN PROGRESS: {str(exception)}"
            )

    # ==========================================================
    # UPDATE ISSUE
    # ==========================================================

    def update_issue(
        self,
        issue_id,
        module,
        category,
        priority,
        description,
        updated_by=None,
    ):
        """
        Update basic Issue information.

        Status and Developer are NOT changed here.
        Workflow status must be changed through the
        dedicated workflow methods.
        """

        issue = self.repository.get_by_id(
            issue_id
        )

        if not issue:
            return self.failed(
                "Issue not found."
            )

        # ------------------------------------------------------
        # Validate Issue data
        # ------------------------------------------------------

        validation = self._validate_issue_data(
            module=module,
            category=category,
            priority=priority,
            description=description,
        )

        if not validation.success:
            return validation

        # ------------------------------------------------------
        # Update fields
        # ------------------------------------------------------

        issue.module = module
        issue.category = category
        issue.priority = priority
        issue.description = description.strip()
        issue.updated_by = updated_by

        try:

            self.repository.update(
                issue
            )

            db.session.commit()

            return self.success(
                message=(
                    f"Issue {issue.issue_no} "
                    "updated successfully."
                ),
                data=issue,
            )

        except Exception as exception:

            db.session.rollback()

            return self.failed(
                "Failed to update Issue: "
                f"{str(exception)}"
            )

    # ==========================================================
    # DELETE ATTACHMENT
    # ==========================================================

    def delete_attachment(
        self,
        attachment_id,
        
    ):
        """
        Permanently delete attachment.

        Process:

            1. Get attachment
            2. Delete physical file
            3. Hard delete database record
            4. Commit transaction
        """

        attachment = (
            self.attachment_repository
            .get_by_id(attachment_id)
        )

        if not attachment:
            return self.failed(
                "Attachment not found."
            )

        file_path = Path(
            attachment.file_path
        )

        try:

            # --------------------------------------------------
            # Delete physical file
            # --------------------------------------------------

            if file_path.exists():
                file_path.unlink()

            # --------------------------------------------------
            # Hard delete database record
            # --------------------------------------------------

            self.attachment_repository.hard_delete(
                attachment
            )

            # --------------------------------------------------
            # Commit
            # --------------------------------------------------

            db.session.commit()

            return self.success(
                message=(
                    "Attachment deleted successfully."
                )
            )

        except Exception as exception:

            db.session.rollback()

            return self.failed(
                "Failed to delete attachment: "
                f"{str(exception)}"
            )