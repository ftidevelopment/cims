from app.core.transaction_manager import TransactionManager
from app.services.base_service import BaseService

from app.repositories.kaizen_repository import (
    KaizenRepository
)

from app.repositories.kaizen_attachment_repository import (
    KaizenAttachmentRepository
)

from app.models.kaizen_attachment import KaizenAttachment


class KaizenAttachmentService(BaseService):
    """
    Service untuk mengelola attachment Kaizen.
    """

    def __init__(self):

        self.kaizen_repository = (
            KaizenRepository()
        )

        self.attachment_repository = (
            KaizenAttachmentRepository()
        )

    # ==================================================
    # GET ATTACHMENTS BY KAIZEN
    # ==================================================

    def get_by_kaizen(self, kaizen_id):

        kaizen = (
            self.kaizen_repository
            .get_by_id(kaizen_id)
        )

        if not kaizen:

            return self.failed(
                "Kaizen not found."
            )

        attachments = (
            self.attachment_repository
            .find_by_kaizen_id(kaizen_id)
        )

        return self.success(
            data=attachments
        )

    # ==================================================
    # GET ATTACHMENT BY ID
    # ==================================================

    def get_by_id(self, attachment_id):

        attachment = (
            self.attachment_repository
            .get_by_id(attachment_id)
        )

        if not attachment:

            return self.failed(
                "Attachment not found."
            )

        return self.success(
            data=attachment
        )

    # ==================================================
    # GET ATTACHMENT BY ID AND KAIZEN
    # ==================================================

    def get_by_id_and_kaizen(
        self,
        attachment_id,
        kaizen_id
    ):

        attachment = (
            self.attachment_repository
            .find_by_id_and_kaizen(
                attachment_id,
                kaizen_id
            )
        )

        if not attachment:

            return self.failed(
                "Attachment not found."
            )

        return self.success(
            data=attachment
        )

    # ==================================================
    # CREATE ATTACHMENT
    # ==================================================

    def create(
        self,
        kaizen_id,
        file_name,
        stored_name,
        file_path,
        file_type,
        file_size=None,
        description=None,
        attachment_type="GENERAL",
    ):
        """
        Membuat record attachment Kaizen.

        File fisik disimpan oleh layer upload/route.
        Service hanya mengelola record database.
        """

        # --------------------------------------------------
        # Check Kaizen
        # --------------------------------------------------

        kaizen = (
            self.kaizen_repository
            .get_by_id(kaizen_id)
        )

        if not kaizen:

            return self.failed(
                "Kaizen not found."
            )

        # --------------------------------------------------
        # Validate Required Fields
        # --------------------------------------------------

        validation = self.validate(
            self.validate_required(
                file_name,
                "File name"
            ),
            self.validate_required(
                stored_name,
                "Stored name"
            ),
            self.validate_required(
                file_path,
                "File path"
            ),
            self.validate_required(
                file_type,
                "File type"
            ),
        )

        if not validation.success:
            return validation

        # --------------------------------------------------
        # Validate Attachment Type
        # --------------------------------------------------

        allowed_attachment_types = {
            "BEFORE",
            "AFTER",
            "GENERAL",
        }

        attachment_type = (
            attachment_type.strip().upper()
            if attachment_type
            else "GENERAL"
        )

        if attachment_type not in allowed_attachment_types:

            return self.failed(
                "Invalid attachment type."
            )

        # --------------------------------------------------
        # Validate File Size
        # --------------------------------------------------

        if file_size is not None:

            if file_size < 0:

                return self.failed(
                    "File size cannot be negative."
                )

        # --------------------------------------------------
        # Get Next Sort Order
        # --------------------------------------------------

        last_sort_order = (
            self.attachment_repository
            .get_last_sort_order(
                kaizen_id
            )
        )

        sort_order = last_sort_order + 1

        # --------------------------------------------------
        # Create Attachment
        # --------------------------------------------------

        attachment = KaizenAttachment(

            kaizen_id=kaizen_id,

            file_name=file_name,

            stored_name=stored_name,

            file_path=file_path,

            file_type=file_type,

            file_size=file_size,

            description=(
                description.strip()
                if description
                else None
            ),

            attachment_type=attachment_type,

            sort_order=sort_order
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------

        try:

            with TransactionManager() as transaction:

                self.attachment_repository.create(
                    attachment
                )

                transaction.flush()

                transaction.refresh(
                    attachment
                )

            return self.success(
                "Attachment uploaded successfully.",
                attachment
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )
    # ==================================================
    # UPDATE DESCRIPTION
    # ==================================================

    def update_description(
        self,
        attachment_id,
        kaizen_id,
        description
    ):

        attachment = (
            self.attachment_repository
            .find_by_id_and_kaizen(
                attachment_id,
                kaizen_id
            )
        )

        if not attachment:

            return self.failed(
                "Attachment not found."
            )

        attachment.description = (
            description.strip()
            if description
            else None
        )

        try:

            with TransactionManager() as transaction:

                self.attachment_repository.update(
                    attachment
                )

                transaction.flush()

                transaction.refresh(
                    attachment
                )

            return self.success(
                "Attachment description updated successfully.",
                attachment
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==================================================
    # DELETE ATTACHMENT
    # ==================================================

    def delete(
        self,
        attachment_id,
        kaizen_id
    ):
        """
        Soft delete attachment dari database.

        File fisik akan ditangani oleh layer
        upload/route.
        """

        attachment = (
            self.attachment_repository
            .find_by_id_and_kaizen(
                attachment_id,
                kaizen_id
            )
        )

        if not attachment:

            return self.failed(
                "Attachment not found."
            )

        try:

            with TransactionManager() as transaction:

                self.attachment_repository.delete(
                    attachment
                )

                transaction.flush()

            return self.success(
                "Attachment deleted successfully.",
                attachment
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==================================================
    # REORDER ATTACHMENT
    # ==================================================

    def reorder(
        self,
        attachment_id,
        kaizen_id,
        sort_order
    ):

        attachment = (
            self.attachment_repository
            .find_by_id_and_kaizen(
                attachment_id,
                kaizen_id
            )
        )

        if not attachment:

            return self.failed(
                "Attachment not found."
            )

        validation = self.validate_positive_number(
            sort_order,
            "Sort order"
        )

        if not validation.success:

            return validation

        attachment.sort_order = sort_order

        try:

            with TransactionManager() as transaction:

                self.attachment_repository.update(
                    attachment
                )

                transaction.flush()

                transaction.refresh(
                    attachment
                )

            return self.success(
                "Attachment order updated successfully.",
                attachment
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )