import os
import uuid

from pathlib import Path

from flask import (
    current_app,
    abort,
    send_file,
)
from werkzeug.utils import secure_filename


class FileService:

    # ==========================================
    # Allowed File Extensions
    # ==========================================

    IMAGE_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "webp",
    }

    ALLOWED_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "webp",
        "pdf",
        "xls",
        "xlsx",
    }

    # ==========================================
    # Save File
    # ==========================================

    @classmethod
    def save(
        cls,
        file,
        folder,
    ):

        if not file or not file.filename:
            return None

        filename = secure_filename(
            file.filename
        )

        if not cls.allowed_extension(
            filename
        ):
            raise ValueError(
                "File type is not allowed."
            )

        extension = (
            Path(filename)
            .suffix
            .lower()
        )

        stored_name = (
            f"{uuid.uuid4().hex}"
            f"{extension}"
        )

        upload_folder = os.path.join(
            current_app.root_path,
            current_app.config[
                "UPLOAD_FOLDER"
            ],
            folder,
        )

        os.makedirs(
            upload_folder,
            exist_ok=True,
        )

        file.save(
            os.path.join(
                upload_folder,
                stored_name,
            )
        )

        return stored_name

    # ==========================================
    # Delete File
    # ==========================================

    @staticmethod
    def delete(
        filename,
        folder,
    ):

        if not filename:
            return

        filepath = os.path.join(
            current_app.root_path,
            current_app.config[
                "UPLOAD_FOLDER"
            ],
            folder,
            filename,
        )

        if os.path.exists(
            filepath
        ):

            os.remove(
                filepath
            )

    # ==========================================
    # Replace File
    # ==========================================

    @classmethod
    def replace(
        cls,
        old_filename,
        new_file,
        folder,
    ):

        cls.delete(
            old_filename,
            folder,
        )

        return cls.save(
            new_file,
            folder,
        )

    # ==========================================
    # Get File Path
    # ==========================================

    @staticmethod
    def get_path(
        filename,
        folder,
    ):

        return os.path.join(
            current_app.root_path,
            current_app.config[
                "UPLOAD_FOLDER"
            ],
            folder,
            filename,
        )

    # ==========================================
    # Get File URL
    # ==========================================

    @staticmethod
    def get_url(
        filename,
        folder,
    ):

        return (
            f"/static/uploads/"
            f"{folder}/"
            f"{filename}"
        )

    # ==========================================
    # Check Image
    # ==========================================

    @classmethod
    def is_image(
        cls,
        filename,
    ):

        if not filename:
            return False

        extension = (
            Path(filename)
            .suffix
            .replace(".", "")
            .lower()
        )

        return (
            extension
            in cls.IMAGE_EXTENSIONS
        )

    # ==========================================
    # Check Extension
    # ==========================================

    @classmethod
    def allowed_extension(
        cls,
        filename,
    ):

        if not filename:
            return False

        extension = (
            Path(filename)
            .suffix
            .replace(".", "")
            .lower()
        )

        return (
            extension
            in cls.ALLOWED_EXTENSIONS
        )

    # ==========================================
    # Get Extension
    # ==========================================

    @staticmethod
    def get_extension(
        filename,
    ):

        if not filename:
            return ""

        return (
            Path(filename)
            .suffix
            .replace(".", "")
            .lower()
        )

    # ==========================================
    # Get Mime Type
    # ==========================================

    @staticmethod
    def get_mime_type(
        file,
    ):

        if not file:
            return ""

        return (
            file.content_type
            or ""
        )

    # ==========================================
    # Get File Size
    # ==========================================

    @staticmethod
    def get_file_size(
        file,
    ):

        if not file:
            return 0

        current = file.stream.tell()

        file.stream.seek(
            0,
            os.SEEK_END,
        )

        size = file.stream.tell()

        file.stream.seek(
            current
        )

        return size


    # ==========================================
    # Exists
    # ==========================================

    @classmethod
    def exists(
        cls,
        filename,
        folder,
    ):

        if not filename:

            return False

        return os.path.exists(

            cls.get_path(
                filename,
                folder,
            )

        )

    # ==========================================
    # Download File
    # ==========================================

    @classmethod
    def download(
        cls,
        filename,
        folder,
        download_name=None,
    ):

        path = cls.get_path(
            filename,
            folder,
        )

        if not os.path.exists(path):

            abort(404)

        return send_file(

            path,

            as_attachment=True,

            download_name=(
                download_name
                or filename
            ),

        )

    # ==========================================
    # Preview File
    # ==========================================

    @classmethod
    def preview(
        cls,
        filename,
        folder,
    ):

        path = cls.get_path(
            filename,
            folder,
        )

        if not os.path.exists(path):

            abort(404)

        return send_file(

            path,

            as_attachment=False,

        )

    # ==========================================
    # Delete If Exists
    # ==========================================

    @classmethod
    def delete_if_exists(
        cls,
        filename,
        folder,
    ):

        if cls.exists(
            filename,
            folder,
        ):

            cls.delete(
                filename,
                folder,
            )


    # ==========================================
    # Original Filename
    # ==========================================

    @staticmethod
    def get_original_filename(
        filename,
    ):

        if not filename:

            return ""

        return secure_filename(
            filename
        )