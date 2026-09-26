from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    send_file
)

from flask_login import login_required

from app.services.improvement_attachment_service import (
    ImprovementAttachmentService
)


# ==================================================
# Blueprint
# ==================================================

improvement_attachment_bp = Blueprint(
    "improvement_attachment",
    __name__,
    url_prefix="/improvements"
)


# ==================================================
# Service
# ==================================================

improvement_attachment_service = (
    ImprovementAttachmentService()
)


# ==================================================
# Upload Attachment
# ==================================================

@improvement_attachment_bp.route(
    "/<int:improvement_id>/attachments",
    methods=["POST"]
)
@login_required
def upload(improvement_id):

    file = request.files.get("file")

    description = request.form.get(
        "description"
    )

    try:

        improvement_attachment_service.create_attachment(
            improvement_id=improvement_id,
            file=file,
            description=description
        )

        flash(
            "Attachment uploaded successfully.",
            "success"
        )

    except ValueError as e:

        flash(
            str(e),
            "danger"
        )

    except Exception:

        flash(
            "Failed to upload attachment.",
            "danger"
        )

    return redirect(
        url_for(
            "improvement.detail",
            improvement_id=improvement_id
        )
    )


# ==================================================
# Download Attachment
# ==================================================

@improvement_attachment_bp.route(
    "/<int:improvement_id>/attachments/"
    "<int:attachment_id>/download",
    methods=["GET"]
)
@login_required
def download(
    improvement_id,
    attachment_id
):

    try:

        attachment, physical_path = (
            improvement_attachment_service
            .get_for_download(
                attachment_id=attachment_id,
                improvement_id=improvement_id
            )
        )

        return send_file(
            physical_path,
            as_attachment=True,
            download_name=attachment.file_name
        )

    except ValueError as e:

        flash(
            str(e),
            "danger"
        )

    except Exception:

        flash(
            "Failed to download attachment.",
            "danger"
        )

    return redirect(
        url_for(
            "improvement.detail",
            improvement_id=improvement_id
        )
    )


# ==================================================
# Delete Attachment
# ==================================================

@improvement_attachment_bp.route(
    "/<int:improvement_id>/attachments/"
    "<int:attachment_id>/delete",
    methods=["POST"]
)
@login_required
def delete(
    improvement_id,
    attachment_id
):

    try:

        improvement_attachment_service.delete_attachment(
            attachment_id=attachment_id,
            improvement_id=improvement_id
        )

        flash(
            "Attachment deleted successfully.",
            "success"
        )

    except ValueError as e:

        flash(
            str(e),
            "danger"
        )

    except Exception:

        flash(
            "Failed to delete attachment.",
            "danger"
        )

    return redirect(
        url_for(
            "improvement.detail",
            improvement_id=improvement_id
        )
    )


@improvement_attachment_bp.route(
    "/<int:improvement_id>/attachments/<int:attachment_id>/preview",
    methods=["GET"]
)
@login_required
def preview(improvement_id, attachment_id):

    try:

        attachment, physical_path = (
            improvement_attachment_service
            .get_for_download(
                attachment_id=attachment_id,
                improvement_id=improvement_id
            )
        )

        return send_file(
            physical_path,
            as_attachment=False,
            download_name=attachment.file_name
        )

    except ValueError as e:

        flash(str(e), "danger")

    except Exception:

        flash("Failed to preview attachment.", "danger")

    return redirect(
        url_for(
            "improvement.detail",
            improvement_id=improvement_id
        )
    )