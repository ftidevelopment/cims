from flask import (
    Blueprint,
    flash,
    redirect,
    url_for,
    request
)

from flask_login import (
    login_required,
    current_user,
)

from app.services.problem_attachment_service import (
    ProblemAttachmentService,
)

problem_attachment_bp = Blueprint(
    "problem_attachment",
    __name__,
    url_prefix="/problem-attachments",
)

problem_attachment_service = (
    ProblemAttachmentService()
)


# ==========================================
# Delete Attachment
# ==========================================

@problem_attachment_bp.route(
    "/<int:attachment_id>/delete",
    methods=["POST"],
)
@login_required
def delete(attachment_id):

    result = (
        problem_attachment_service.delete(
            attachment_id=attachment_id,
        )
    )

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(request.referrer or url_for("problem.index"))


# ==========================================
# Restore Attachment
# ==========================================

@problem_attachment_bp.route(
    "/<int:attachment_id>/restore",
    methods=["POST"],
)
@login_required
def restore(attachment_id):

    result = (
        problem_attachment_service.restore(
            attachment_id=attachment_id,
            restored_by=current_user.id,
        )
    )

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(request.referrer or url_for("problem.index"))


# ==========================================
# Download Attachment
# ==========================================

@problem_attachment_bp.route(
    "/<int:attachment_id>/download",
)
@login_required
def download(attachment_id):

    return problem_attachment_service.download(
        attachment_id
    )


# ==========================================
# Preview Attachment
# ==========================================

@problem_attachment_bp.route(
    "/<int:attachment_id>/preview",
)
@login_required
def preview(attachment_id):

    return problem_attachment_service.preview(
        attachment_id
    )

@problem_attachment_bp.route(
    "/<int:attachment_id>",
)
@login_required
def show(attachment_id):

    attachment = (
        problem_attachment_service.get_by_id(
            attachment_id
        )
    )

    return attachment


@problem_attachment_bp.route(
    "/problem/<int:problem_id>",
)
@login_required
def by_problem(problem_id):

    attachments = (
        problem_attachment_service.get_by_problem(
            problem_id
        )
    )

    return attachments