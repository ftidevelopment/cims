from io import BytesIO
from pathlib import Path
from datetime import datetime

from flask import (
    current_app,
    render_template,
)

from weasyprint import HTML


class PDFReportService:
    """
    Service untuk generate PDF report menggunakan WeasyPrint.
    """

    # ==================================================
    # PROBLEM PDF REPORT
    # ==================================================

    @staticmethod
    def generate_problem_report(
        problem,
        printed_by=None,
    ):
        """
        Generate Problem Report PDF.
        """

        # ==================================================
        # Attachment Directory
        # ==================================================

        attachment_directory = (
            Path(current_app.root_path)
            / "static"
            / "uploads"
            / "problem"
        )

        # ==================================================
        # Image Attachments
        # ==================================================

        attachment_images = {}

        for attachment in problem.attachments:

            if not attachment.is_image:
                continue

            file_path = (
                attachment_directory
                / attachment.stored_name
            )

            if not file_path.exists():
                continue

            try:

                attachment_images[
                    attachment.id
                ] = file_path.as_uri()

            except ValueError:

                continue

        # ==================================================
        # Logo
        # ==================================================

        logo_path = (
            Path(current_app.root_path)
            / "static"
            / "img"
            / "cims_logo.png"
        )

        logo_uri = None

        if logo_path.exists():

            try:

                logo_uri = logo_path.as_uri()

            except ValueError:

                logo_uri = None

        # ==================================================
        # Render HTML
        # ==================================================

        html_content = render_template(

            "reports/problem_pdf.html",

            problem=problem,

            attachment_images=attachment_images,

            logo_uri=logo_uri,

            printed_by=printed_by,

            print_datetime=datetime.now(),

        )

        # ==================================================
        # Generate PDF
        # ==================================================

        pdf_file = BytesIO()

        HTML(
            string=html_content,
            base_url=current_app.root_path,
        ).write_pdf(
            pdf_file
        )

        # ==================================================
        # Reset File Pointer
        # ==================================================

        pdf_file.seek(0)

        return pdf_file


    # ==================================================
    # IMPROVEMENT PDF REPORT
    # ==================================================

    @staticmethod
    def generate_improvement_report(
        improvement,
        printed_by=None,
        created_by_name=None,
    ):
        """
        Generate Improvement Report PDF.
        """

        # ==================================================
        # Image Attachments
        # ==================================================

        attachment_images = {}

        for attachment in improvement.attachments:

            # --------------------------------------------------
            # Hanya image
            # --------------------------------------------------

            file_type = (
                attachment.file_type or ""
            ).lower()

            is_image = file_type.startswith(
                "image/"
            )

            if not is_image:
                continue

            # --------------------------------------------------
            # Gunakan file_path dari database
            # --------------------------------------------------

            file_path = Path(
                attachment.file_path
            )

            # Jika relative path
            if not file_path.is_absolute():

                file_path = (
                    Path(
                        current_app.root_path
                    )
                    / file_path
                )

            # --------------------------------------------------
            # Pastikan file ada
            # --------------------------------------------------

            if not file_path.exists():
                continue

            try:

                attachment_images[
                    attachment.id
                ] = file_path.as_uri()

            except ValueError:

                continue

        # ==================================================
        # Logo
        # ==================================================

        logo_path = (
            Path(current_app.root_path)
            / "static"
            / "img"
            / "cims_logo.png"
        )

        logo_uri = None

        if logo_path.exists():

            try:

                logo_uri = logo_path.as_uri()

            except ValueError:

                logo_uri = None

        # ==================================================
        # Render HTML
        # ==================================================

        html_content = render_template(

            "reports/improvement_pdf.html",

            improvement=improvement,

            attachment_images=attachment_images,

            logo_uri=logo_uri,

            printed_by=printed_by,

            created_by_name=created_by_name,

            print_datetime=datetime.now(),

        )

        # ==================================================
        # Generate PDF
        # ==================================================

        pdf_file = BytesIO()

        HTML(
            string=html_content,
            base_url=current_app.root_path,
        ).write_pdf(
            pdf_file
        )

        # ==================================================
        # Reset Pointer
        # ==================================================

        pdf_file.seek(0)

        return pdf_file


    # =========================================================
    # KAIZEN PDF REPORT
    # =========================================================

    @staticmethod
    def generate_kaizen_report(
        kaizen,
        printed_by=None,
    ):
        """
        Generate Kaizen Report PDF.
        """

        # ==================================================
        # Image Attachments
        # ==================================================

        attachment_images = {}

        for attachment in kaizen.attachments:

            # --------------------------------------------------
            # Pastikan file_path tersedia
            # --------------------------------------------------

            if not attachment.file_path:
                continue

            # --------------------------------------------------
            # Detect image berdasarkan file_type
            # --------------------------------------------------

            file_type = (
                attachment.file_type or ""
            ).lower().strip()

            is_image = file_type.startswith(
                "image/"
            )

            if not is_image:
                continue

            # --------------------------------------------------
            # File Path
            # --------------------------------------------------

            file_path = Path(
                attachment.file_path
            )

            # --------------------------------------------------
            # Jika relative path
            # --------------------------------------------------

            if not file_path.is_absolute():

                file_path = (
                    Path(
                        current_app.root_path
                    )
                    / file_path
                )

            # --------------------------------------------------
            # Pastikan file ada
            # --------------------------------------------------

            if not file_path.exists():

                current_app.logger.warning(
                    "Kaizen attachment file not found: %s",
                    file_path,
                )

                continue

            # --------------------------------------------------
            # Convert ke URI
            # --------------------------------------------------

            try:

                attachment_images[
                    attachment.id
                ] = file_path.as_uri()

            except ValueError:

                current_app.logger.warning(
                    "Unable to convert Kaizen attachment "
                    "to URI: %s",
                    file_path,
                )

                continue

        # ==================================================
        # Logo
        # ==================================================

        logo_path = (
            Path(current_app.root_path)
            / "static"
            / "img"
            / "cims_logo.png"
        )

        logo_uri = None

        if logo_path.exists():

            try:

                logo_uri = logo_path.as_uri()

            except ValueError:

                logo_uri = None

        # ==================================================
        # Render HTML
        # ==================================================

        html_content = render_template(

            "reports/kaizen_pdf.html",

            kaizen=kaizen,

            attachment_images=attachment_images,

            logo_uri=logo_uri,

            printed_by=printed_by,

            print_datetime=datetime.now(),

        )

        # ==================================================
        # Generate PDF
        # ==================================================

        pdf_file = BytesIO()

        HTML(
            string=html_content,
            base_url=current_app.root_path,
        ).write_pdf(
            pdf_file
        )

        # ==================================================
        # Reset File Pointer
        # ==================================================

        pdf_file.seek(0)

        return pdf_file


    # ==================================================
    # LOGO URI HELPER
    # ==================================================

    @staticmethod
    def _get_logo_uri():

        logo_path = (
            Path(current_app.root_path)
            / "static"
            / "img"
            / "cims_logo.png"
        )

        if not logo_path.exists():

            return None

        try:

            return logo_path.as_uri()

        except ValueError:

            return None