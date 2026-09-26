import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.improvement_attachment import ImprovementAttachment
from app.repositories.improvement_attachment_repository import (
    ImprovementAttachmentRepository
)
from app.repositories.improvement_repository import ImprovementRepository


class ImprovementAttachmentService:

    # --------------------------------------------------
    # Allowed File Extensions
    # --------------------------------------------------

    ALLOWED_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "webp",
        "pdf",
        "xls",
        "xlsx"
    }

    # --------------------------------------------------
    # Maximum File Size
    # --------------------------------------------------
    # 10 MB

    MAX_FILE_SIZE = 10 * 1024 * 1024

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------

    def __init__(self):

        self.repository = (
            ImprovementAttachmentRepository()
        )

        self.improvement_repository = (
            ImprovementRepository()
        )

    # --------------------------------------------------
    # Get All Attachments
    # --------------------------------------------------

    def get_by_improvement(self, improvement_id):

        return (
            self.repository
            .find_by_improvement_id(
                improvement_id
            )
        )

    # --------------------------------------------------
    # Get Attachment
    # --------------------------------------------------

    def get_by_id(self, attachment_id):

        return (
            self.repository
            .get_by_id(
                attachment_id
            )
        )


    # --------------------------------------------------
    # Get Attachment For Download
    # --------------------------------------------------

    def get_for_download(
        self,
        attachment_id,
        improvement_id
    ):

        attachment = (
            self.repository
            .find_by_id_and_improvement(
                attachment_id,
                improvement_id
            )
        )

        if not attachment:
            raise ValueError(
                "Attachment not found."
            )

        physical_path = (
            self._get_physical_path(
                attachment.file_path
            )
        )

        if not physical_path:
            raise ValueError(
                "Attachment file path is not available."
            )

        if not os.path.isfile(
            physical_path
        ):
            raise ValueError(
                "Attachment file not found on server."
            )

        return attachment, physical_path

    # --------------------------------------------------
    # Validate Extension
    # --------------------------------------------------

    def _get_extension(self, filename):

        if not filename:
            raise ValueError(
                "File name is required."
            )

        filename = secure_filename(
            filename
        )

        if "." not in filename:
            raise ValueError(
                "File must have an extension."
            )

        extension = (
            filename
            .rsplit(".", 1)[1]
            .lower()
        )

        if extension not in self.ALLOWED_EXTENSIONS:

            raise ValueError(
                "File type is not allowed. "
                "Allowed types: JPG, JPEG, PNG, "
                "WEBP, PDF, XLS, XLSX."
            )

        return extension

    # --------------------------------------------------
    # Validate File Size
    # --------------------------------------------------

    def _validate_file_size(self, file):

        file.seek(0, os.SEEK_END)

        file_size = file.tell()

        file.seek(0)

        if file_size <= 0:

            raise ValueError(
                "File is empty."
            )

        if file_size > self.MAX_FILE_SIZE:

            raise ValueError(
                "File size exceeds the maximum "
                "allowed size of 10 MB."
            )

        return file_size

    # --------------------------------------------------
    # Generate Storage Name
    # --------------------------------------------------

    def _generate_stored_name(
        self,
        extension
    ):

        return (
            f"{uuid.uuid4().hex}"
            f".{extension}"
        )

    # --------------------------------------------------
    # Get Upload Directory
    # --------------------------------------------------

    def _get_upload_directory(self):

        upload_directory = os.path.join(
            current_app.static_folder,
            "uploads",
            "improvements"
        )

        os.makedirs(
            upload_directory,
            exist_ok=True
        )

        return upload_directory

    # --------------------------------------------------
    # Get Physical File Path
    # --------------------------------------------------

    def _get_physical_path(self, file_path):

        if not file_path:
            return None

        return os.path.join(
            current_app.static_folder,
            file_path
        )

    # --------------------------------------------------
    # Create Attachment
    # --------------------------------------------------

    def create_attachment(
        self,
        improvement_id,
        file,
        description=None
    ):

        # --------------------------------------------------
        # Validate Improvement
        # --------------------------------------------------

        improvement = (
            self.improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            raise ValueError(
                "Improvement not found."
            )

        # --------------------------------------------------
        # Check Problem Status
        # --------------------------------------------------

        if (
            improvement.problem
            and improvement.problem.status == "Closed"
        ):

            raise ValueError(
                "Cannot upload attachment "
                "because the problem is closed."
            )

        # --------------------------------------------------
        # Validate File
        # --------------------------------------------------

        if not file:

            raise ValueError(
                "Please select a file."
            )

        if not file.filename:

            raise ValueError(
                "File name is required."
            )

        # --------------------------------------------------
        # Validate Extension
        # --------------------------------------------------

        extension = self._get_extension(
            file.filename
        )

        # --------------------------------------------------
        # Validate File Size
        # --------------------------------------------------

        file_size = self._validate_file_size(
            file
        )

        # --------------------------------------------------
        # Prepare File Name
        # --------------------------------------------------

        original_file_name = secure_filename(
            file.filename
        )

        stored_name = (
            self._generate_stored_name(
                extension
            )
        )

        # --------------------------------------------------
        # Prepare Directory
        # --------------------------------------------------

        upload_directory = (
            self._get_upload_directory()
        )

        # --------------------------------------------------
        # Physical File Path
        # --------------------------------------------------

        physical_path = os.path.join(
            upload_directory,
            stored_name
        )

        # --------------------------------------------------
        # Database Relative Path
        # --------------------------------------------------

        file_path = os.path.join(
            "uploads",
            "improvements",
            stored_name
        ).replace("\\", "/")

        # --------------------------------------------------
        # Get Sort Order
        # --------------------------------------------------

        last_sort_order = (
            self.repository
            .get_last_sort_order(
                improvement_id
            )
        )

        sort_order = (
            last_sort_order + 1
        )

        # --------------------------------------------------
        # Save Physical File
        # --------------------------------------------------

        try:

            file.save(
                physical_path
            )

            # --------------------------------------------------
            # Create Database Record
            # --------------------------------------------------

            attachment = ImprovementAttachment(

                improvement_id=improvement_id,

                file_name=original_file_name,

                stored_name=stored_name,

                file_path=file_path,

                file_type=extension,

                file_size=file_size,

                description=(
                    description.strip()
                    if description
                    else None
                ),

                sort_order=sort_order

            )

            self.repository.create(
                attachment
            )

            db.session.commit()

            return attachment

        except Exception:

            db.session.rollback()

            # --------------------------------------------------
            # Remove Physical File
            # if Database Save Failed
            # --------------------------------------------------

            if os.path.exists(
                physical_path
            ):

                try:

                    os.remove(
                        physical_path
                    )

                except OSError:

                    current_app.logger.exception(
                        "Failed to remove uploaded "
                        "file after database error: %s",
                        physical_path
                    )

            raise

    # --------------------------------------------------
    # Delete Attachment
    # --------------------------------------------------

    def delete_attachment(
        self,
        attachment_id,
        improvement_id
    ):

        # --------------------------------------------------
        # Get Attachment
        # --------------------------------------------------

        attachment = (
            self.repository
            .find_by_id_and_improvement(
                attachment_id,
                improvement_id
            )
        )

        if not attachment:

            raise ValueError(
                "Attachment not found."
            )

        # --------------------------------------------------
        # Get Improvement
        # --------------------------------------------------

        improvement = (
            self.improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            raise ValueError(
                "Improvement not found."
            )

        # --------------------------------------------------
        # Check Problem Status
        # --------------------------------------------------

        if (
            improvement.problem
            and improvement.problem.status == "Closed"
        ):

            raise ValueError(
                "Cannot delete attachment "
                "because the problem is closed."
            )

        # --------------------------------------------------
        # Get Physical File Path
        # --------------------------------------------------

        physical_path = (
            self._get_physical_path(
                attachment.file_path
            )
        )

        # --------------------------------------------------
        # Delete Database Record
        # --------------------------------------------------

        try:

            db.session.delete(
                attachment
            )

            db.session.commit()

        except Exception:

            db.session.rollback()

            raise

        # --------------------------------------------------
        # Delete Physical File
        # --------------------------------------------------

        if (
            physical_path
            and os.path.exists(
                physical_path
            )
        ):

            try:

                os.remove(
                    physical_path
                )

            except OSError:

                current_app.logger.exception(
                    "Failed to delete attachment "
                    "file: %s",
                    physical_path
                )

        return True