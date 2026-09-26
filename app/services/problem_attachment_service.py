from app.services.base_service import (
    BaseService,
)

from app.core.transaction_manager import (
    TransactionManager,
)

from app.core.upload_folder import (
    UploadFolder,
)

from app.repositories.problem_attachment_repository import (
    ProblemAttachmentRepository,
)

from app.services.file_service import (
    FileService,
)


class ProblemAttachmentService(
    BaseService
):

    def __init__(self):

        super().__init__()

        self.repository = (
            ProblemAttachmentRepository()
        )

    # ==========================================
    # Get
    # ==========================================

    def get_by_id(
        self,
        attachment_id,
    ):

        return self.repository.get_by_id(
            attachment_id
        )

    def get_by_problem(
        self,
        problem_id,
    ):

        return self.repository.get_by_problem(
            problem_id
        )

    # ==========================================
    # Download
    # ==========================================

    def download(
        self,
        attachment_id,
    ):

        try:

            attachment = (
                self.repository.get_by_id(
                    attachment_id
                )
            )

            self.validate_exists(
                attachment,
                "Attachment",
            )

            return FileService.download(

                filename=attachment.stored_name,

                folder=UploadFolder.PROBLEM,

                download_name=attachment.original_name,

            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Preview
    # ==========================================

    def preview(
        self,
        attachment_id,
    ):

        try:

            attachment = (
                self.repository.get_by_id(
                    attachment_id
                )
            )

            self.validate_exists(
                attachment,
                "Attachment",
            )

            return FileService.preview(

                filename=attachment.stored_name,

                folder=UploadFolder.PROBLEM,

            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Delete
    # ==========================================

    # ==========================================
    # Delete
    # ==========================================

    def delete(
        self,
        attachment_id,
    ):

        try:

            attachment = (
                self.repository.get_by_id(
                    attachment_id
                )
            )

            self.validate_exists(
                attachment,
                "Attachment",
            )

            with TransactionManager():

                FileService.delete_if_exists(
                    filename=attachment.stored_name,
                    folder=UploadFolder.PROBLEM,
                )

                self.repository.hard_delete(
                    attachment
                )

            return self.success(
                "Attachment deleted successfully."
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
        attachment_id,
        restored_by=None,
    ):

        try:

            attachment = (
                self.repository.get_inactive_by_id(
                    attachment_id
                )
            )

            self.validate_exists(
                attachment,
                "Attachment",
            )

            with TransactionManager():

                attachment.updated_by = (
                    restored_by
                )

                attachment.is_active = True

                self.repository.update(
                    attachment
                )

            return self.success(
                "Attachment restored successfully."
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Count
    # ==========================================

    def count_by_problem(
        self,
        problem_id,
    ):

        return self.repository.count_by_problem(
            problem_id
        )

    # ==========================================
    # Exists
    # ==========================================

    def exists(
        self,
        attachment_id,
    ):

        return self.repository.exists(
            attachment_id
        )