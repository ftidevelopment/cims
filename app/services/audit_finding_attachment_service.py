import os
import uuid
from pathlib import Path

from flask import current_app

from app.extensions import db
from app.models.audit_finding_attachment import AuditFindingAttachment
from app.repositories.audit_finding_attachment_repository import (
    AuditFindingAttachmentRepository
)
from app.repositories.audit_finding_repository import AuditFindingRepository
from app.core.service_result import ServiceResult
from app.core.transaction_manager import TransactionManager


class AuditFindingAttachmentService:

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
        "ppt",
        "pptx",
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    ATTACHMENT_TYPES = [
        "FINDING_EVIDENCE",
        "CORRECTIVE_ACTION",
        "VERIFICATION",
        "OTHER",
    ]

    def __init__(self):
        self.repository = AuditFindingAttachmentRepository()
        self.finding_repository = AuditFindingRepository()

    # =========================================================
    # FILE VALIDATION
    # =========================================================

    def _get_extension(self, filename: str) -> str:
        return Path(filename).suffix.lower().lstrip(".")

    def _validate_file(self, file):
        if not file:
            raise ValueError("File is required.")

        if not file.filename:
            raise ValueError("File name is empty.")

        extension = self._get_extension(file.filename)

        if extension not in self.ALLOWED_EXTENSIONS:
            allowed = ", ".join(
                sorted(self.ALLOWED_EXTENSIONS)
            )
            raise ValueError(
                f"File type '.{extension}' is not allowed. "
                f"Allowed types: {allowed}."
            )

        return extension

    # =========================================================
    # STORAGE PATH
    # =========================================================

    def _get_upload_root(self):
        """
        Storage:
        <project>/uploads/audit_findings/
        """

        upload_root = current_app.config.get(
            "AUDIT_FINDING_UPLOAD_FOLDER"
        )

        if upload_root:
            return Path(upload_root)

        # Default:
        # project_root/uploads/audit_findings
        project_root = Path(current_app.root_path).parent

        return project_root / "uploads" / "audit_findings"

    def _get_finding_folder(self, finding):
        folder = (
            self._get_upload_root()
            / finding.finding_no
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        return folder

    # =========================================================
    # CREATE
    # =========================================================

    def create(
        self,
        audit_finding_id: int,
        file,
        description: str = None,
        attachment_type: str = "FINDING_EVIDENCE",
    ):
        try:
            # -------------------------------------------------
            # Validate finding
            # -------------------------------------------------
            finding = self.finding_repository.get_by_id(
                audit_finding_id
            )

            if not finding:
                return ServiceResult(
                    success=False,
                    message="Audit finding not found."
                )

            # -------------------------------------------------
            # Validate file
            # -------------------------------------------------
            extension = self._validate_file(file)

            # -------------------------------------------------
            # Validate attachment type
            # -------------------------------------------------
            if attachment_type not in self.ATTACHMENT_TYPES:
                return ServiceResult(
                    success=False,
                    message="Invalid attachment type."
                )

            # -------------------------------------------------
            # Validate file size
            # -------------------------------------------------
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > self.MAX_FILE_SIZE:
                return ServiceResult(
                    success=False,
                    message="File size must not exceed 10 MB."
                )

            # -------------------------------------------------
            # Prepare storage
            # -------------------------------------------------
            finding_folder = self._get_finding_folder(finding)

            unique_name = (
                f"{uuid.uuid4().hex}.{extension}"
            )

            physical_path = (
                finding_folder / unique_name
            )

            # -------------------------------------------------
            # Save physical file
            # -------------------------------------------------
            file.save(str(physical_path))

            # -------------------------------------------------
            # Database path
            # -------------------------------------------------
            relative_path = os.path.relpath(
                physical_path,
                self._get_upload_root()
            )

            # Convert Windows "\" to "/"
            relative_path = relative_path.replace(
                "\\",
                "/"
            )

            # -------------------------------------------------
            # Create DB record
            # -------------------------------------------------
            attachment = AuditFindingAttachment(
                audit_finding_id=audit_finding_id,
                original_filename=file.filename,
                description=description.strip()
                if description
                else None,
                stored_filename=unique_name,
                file_path=relative_path,
                file_extension=extension,
                mime_type=file.mimetype,
                file_size=file_size,
                attachment_type=attachment_type,
            )

            with TransactionManager():
                self.repository.create(attachment)

            return ServiceResult(
                success=True,
                message="Attachment uploaded successfully.",
                data=attachment
            )

        except Exception as e:

            # -------------------------------------------------
            # Cleanup physical file if DB operation fails
            # -------------------------------------------------
            try:
                if "physical_path" in locals():
                    if physical_path.exists():
                        physical_path.unlink()
            except Exception:
                pass

            db.session.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to upload attachment: {str(e)}"
            )

    # =========================================================
    # GET
    # =========================================================

    def get_by_id(self, attachment_id: int):
        return self.repository.get_by_id(
            attachment_id
        )

    def get_by_finding(self, audit_finding_id: int):
        return self.repository.get_by_finding(
            audit_finding_id
        )

    def get_by_type(
        self,
        audit_finding_id: int,
        attachment_type: str
    ):
        return self.repository.get_by_type(
            audit_finding_id,
            attachment_type
        )

    # =========================================================
    # DELETE
    # =========================================================

    def delete(
        self,
        attachment_id: int,
        audit_finding_id: int = None
    ):
        attachment = None

        try:

            # -------------------------------------------------
            # Get attachment
            # -------------------------------------------------
            if audit_finding_id is not None:

                attachment = (
                    self.repository.get_by_id_for_finding(
                        attachment_id,
                        audit_finding_id
                    )
                )

            else:

                attachment = self.repository.get_by_id(
                    attachment_id
                )

            if not attachment:
                return ServiceResult(
                    success=False,
                    message="Attachment not found."
                )

            # -------------------------------------------------
            # Physical file path
            # -------------------------------------------------
            physical_path = (
                self._get_upload_root()
                / attachment.file_path
            )

            # -------------------------------------------------
            # Delete physical file
            # -------------------------------------------------
            if physical_path.exists():
                physical_path.unlink()

            # -------------------------------------------------
            # Hard delete database record
            # -------------------------------------------------
            with TransactionManager():
                self.repository.hard_delete(attachment)

            # -------------------------------------------------
            # Remove empty finding folder
            # -------------------------------------------------
            try:
                finding_folder = physical_path.parent

                if finding_folder.exists():
                    if not any(finding_folder.iterdir()):
                        finding_folder.rmdir()

            except Exception:
                pass

            return ServiceResult(
                success=True,
                message="Attachment deleted successfully."
            )

        except Exception as e:

            db.session.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to delete attachment: {str(e)}"
            )