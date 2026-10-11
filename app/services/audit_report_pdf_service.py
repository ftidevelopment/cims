from io import BytesIO
from pathlib import Path

from flask import current_app, render_template
from weasyprint import HTML

from app.models.audit import Audit


class AuditReportPDFService:

    @staticmethod
    def generate(audit_id):

        # ==================================================
        # Get Audit
        # ==================================================

        audit = Audit.query.get(audit_id)

        if not audit:
            raise ValueError("Audit not found.")

        # ==================================================
        # Assignments
        # ==================================================

        assignments = audit.audit_assignments or []

        # ==================================================
        # Executions
        # ==================================================

        executions = []

        for assignment in assignments:

            for execution in (
                assignment.audit_executions or []
            ):

                executions.append(
                    {
                        "assignment": assignment,
                        "execution": execution,
                        "items": execution.items or [],
                        "findings": execution.findings or [],
                    }
                )

        # ==================================================
        # Summary
        # ==================================================

        total_assignments = len(assignments)

        total_executions = len(executions)

        total_checklist_items = sum(
            len(execution_data["items"])
            for execution_data in executions
        )

        total_findings = sum(
            len(execution_data["findings"])
            for execution_data in executions
        )

        # ==================================================
        # Logo
        # ==================================================

        # ==================================================
        # CIMS Logo
        # ==================================================

        cims_logo_path = (
            Path(current_app.root_path)
            / "static"
            / "img"
            / "cims_logo.png"
        )

        cims_logo_uri = None

        if cims_logo_path.exists():

            try:

                cims_logo_uri = cims_logo_path.as_uri()

            except ValueError:

                cims_logo_uri = None


        # ==================================================
        # FOXCONN Logo
        # ==================================================

        foxconn_logo_path = (
            Path(current_app.root_path)
            / "static"
            / "img"
            / "foxconn_company.png"
        )

        foxconn_logo_uri = None

        if foxconn_logo_path.exists():

            try:

                foxconn_logo_uri = foxconn_logo_path.as_uri()

            except ValueError:

                foxconn_logo_uri = None
        # ==================================================
        # Render HTML
        # ==================================================

        html_string = render_template(
            "audit/pdf/audit_report.html",

            audit=audit,

            assignments=assignments,

            executions=executions,

            total_assignments=total_assignments,

            total_executions=total_executions,

            total_checklist_items=total_checklist_items,

            total_findings=total_findings,

            cims_logo_uri=cims_logo_uri,

            foxconn_logo_uri=foxconn_logo_uri,
        )

        # ==================================================
        # Generate PDF
        # ==================================================

        pdf_file = BytesIO()

        HTML(
            string=html_string,
            base_url=current_app.root_path,
        ).write_pdf(
            pdf_file
        )

        # ==================================================
        # Reset File Pointer
        # ==================================================

        pdf_file.seek(0)

        return pdf_file