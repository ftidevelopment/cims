from pathlib import Path
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)
from app.extensions import db

from flask_login import login_required, current_user

from app.services.issue_service import IssueService
from app.services.authorization_service import AuthorizationService
from app.services.issue_clarification_service import (
    IssueClarificationService,
)

# ==========================================================
# BLUEPRINT
# ==========================================================

issue_bp = Blueprint(
    "issue",
    __name__,
    url_prefix="/issues",
)


# ==========================================================
# SERVICES / REPOSITORIES
# ==========================================================

issue_service = IssueService()
authorization_service = AuthorizationService()


# ==========================================================
# INDEX / LIST
# ==========================================================

@issue_bp.route("/")
@login_required
def index():
    """
    Issue list page.

    Supports:
        - keyword search
        - pagination
        - sorting
    """

    keyword = request.args.get(
        "keyword",
        "",
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int,
    )

    sort_by = request.args.get(
        "sort_by",
        "created_at",
    )

    sort_order = request.args.get(
        "sort_order",
        "desc",
    )

    issues = issue_service.get_all(
        keyword=keyword,
        is_active=True,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "issue/index.html",
        issues=issues,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        per_page=per_page,
        now=datetime.now(),
    )


# ==========================================================
# CREATE
# ==========================================================

@issue_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """
    Create new Issue.

    Requestor is automatically taken from
    the logged-in user.
    """

    if request.method == "GET":

        return render_template(
            "issue/create.html",
            modules=issue_service.get_modules(),
            categories=issue_service.get_categories(),
            priorities=issue_service.get_priorities(),
        )

    # ------------------------------------------------------
    # Form data
    # ------------------------------------------------------

    module = request.form.get(
        "module",
        "",
    ).strip()

    category = request.form.get(
        "category",
        "",
    ).strip()

    priority = request.form.get(
        "priority",
        "",
    ).strip()

    description = request.form.get(
        "description",
        "",
    ).strip()

    # ------------------------------------------------------
    # Requestor
    # ------------------------------------------------------

    requestor_employee_id = (
        current_user.employee_id
    )

    # ------------------------------------------------------
    # Attachments
    # ------------------------------------------------------

    attachments = request.files.getlist(
        "attachments"
    )
    attachment_descriptions = request.form.getlist(
        "attachment_descriptions"
    )

    # Remove empty file input
    attachments = [
        file
        for file in attachments
        if file and file.filename
    ]

    # ------------------------------------------------------
    # Created by
    # ------------------------------------------------------

    created_by = getattr(
        current_user,
        "username",
        None,
    )

    # ------------------------------------------------------
    # Create Issue
    # ------------------------------------------------------

    result = issue_service.create_issue(
        module=module,
        category=category,
        priority=priority,
        description=description,
        requestor_employee_id=requestor_employee_id,
        attachments=attachments,
        attachment_descriptions=attachment_descriptions,
        created_by=created_by,
    )

    # ------------------------------------------------------
    # Failed
    # ------------------------------------------------------

    if not result.success:

        flash(
            result.message,
            "danger",
        )

        return render_template(
            "issue/create.html",
            modules=issue_service.get_modules(),
            categories=issue_service.get_categories(),
            priorities=issue_service.get_priorities(),
            form_data=request.form,
        )

    # ------------------------------------------------------
    # Success
    # ------------------------------------------------------

    flash(
        result.message,
        "success",
    )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=result.data.id,
        )
    )


# ==========================================================
# DETAIL
# ==========================================================

@issue_bp.route("/<int:issue_id>")
@login_required
def detail(issue_id):

    issue = issue_service.get_by_id(issue_id)

    if not issue:
        flash("Issue not found.", "danger")
        return redirect(url_for("issue.index"))

    attachments = issue_service.get_attachments(issue.id)
    clarification_service = IssueClarificationService()

    clarifications = clarification_service.get_by_issue(
        issue.id
    )

    can_edit = authorization_service.can_edit_issue(
        user=current_user,
        issue=issue,
    )

    can_add_attachment = authorization_service.can_add_issue_attachment(
        user=current_user,
        issue=issue,
    )

    can_delete_attachment = authorization_service.can_delete_issue_attachment(
        user=current_user,
        issue=issue,
    )

    can_delete = authorization_service.can_delete_issue(
        user=current_user,
        issue=issue,
    )

    can_manage_workflow = authorization_service._is_admin(
        current_user
    )

    return render_template(
        "issue/detail.html",
        issue=issue,
        attachments=attachments,
        clarifications=clarifications,
        now=datetime.now(),
        can_edit=can_edit,
        can_add_attachment=can_add_attachment,
        can_delete_attachment=can_delete_attachment,
        can_delete=can_delete,
        can_manage_workflow=can_manage_workflow,
    )


# ==========================================================
# UPDATE
# ==========================================================
@issue_bp.route(
    "/<int:issue_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(issue_id):
    """
    Update basic Issue information.

    Authorization:
    - ADMIN can edit all Issues.
    - Issue creator/requestor can edit own Issue.
    - Other users are read-only.

    Status and Developer are NOT changed here.
    """

    # ======================================================
    # GET ISSUE
    # ======================================================

    issue = issue_service.get_by_id(
        issue_id
    )

    if not issue:

        flash(
            "Issue not found.",
            "danger",
        )

        return redirect(
            url_for("issue.index")
        )

    # ======================================================
    # AUTHORIZATION
    # ======================================================

    if not authorization_service.can_edit_issue(
        user=current_user,
        issue=issue,
    ):

        flash(
            "You do not have permission to edit this Issue.",
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue.id,
            )
        )

    # ======================================================
    # GET
    # ======================================================

    if request.method == "GET":

        return render_template(
            "issue/edit.html",
            issue=issue,
            modules=issue_service.get_modules(),
            categories=issue_service.get_categories(),
            priorities=issue_service.get_priorities(),
        )

    # ======================================================
    # POST
    # ======================================================

    module = request.form.get(
        "module",
        "",
    ).strip()

    category = request.form.get(
        "category",
        "",
    ).strip()

    priority = request.form.get(
        "priority",
        "",
    ).strip()

    description = request.form.get(
        "description",
        "",
    ).strip()

    updated_by = getattr(
        current_user,
        "username",
        None,
    )

    # ======================================================
    # UPDATE ISSUE
    # ======================================================

    result = issue_service.update_issue(
        issue_id=issue_id,
        module=module,
        category=category,
        priority=priority,
        description=description,
        updated_by=updated_by,
    )

    # ======================================================
    # FAILED
    # ======================================================

    if not result.success:

        flash(
            result.message,
            "danger",
        )

        return render_template(
            "issue/edit.html",
            issue=issue,
            modules=issue_service.get_modules(),
            categories=issue_service.get_categories(),
            priorities=issue_service.get_priorities(),
        )

    # ======================================================
    # SUCCESS
    # ======================================================

    flash(
        result.message,
        "success",
    )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=issue.id,
        )
    )


# ==========================================================
# START ISSUE
# ==========================================================

@issue_bp.route(
    "/<int:issue_id>/start",
    methods=["POST"],
)
@login_required
def start(issue_id):
    """
    Workflow:

        OPEN → IN_PROGRESS

    Developer is the logged-in user.
    """

    developer_employee_id = (
        current_user.employee_id
    )

    updated_by = getattr(
        current_user,
        "username",
        None,
    )

    result = issue_service.start_issue(
        issue_id=issue_id,
        developer_employee_id=developer_employee_id,
        updated_by=updated_by,
    )

    if not result.success:

        flash(
            result.message,
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue_id,
            )
        )

    flash(
        result.message,
        "success",
    )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=issue_id,
        )
    )


# ==========================================================
# FINISH ISSUE
# ==========================================================

@issue_bp.route(
    "/<int:issue_id>/finish",
    methods=["POST"],
)
@login_required
def finish(issue_id):
    """
    Workflow:

        IN_PROGRESS → FINISH
    """

    updated_by = getattr(
        current_user,
        "username",
        None,
    )

    result = issue_service.finish_issue(
        issue_id=issue_id,
        updated_by=updated_by,
    )

    if not result.success:

        flash(
            result.message,
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue_id,
            )
        )

    flash(
        result.message,
        "success",
    )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=issue_id,
        )
    )


# ==========================================================
# CLOSE ISSUE
# ==========================================================

@issue_bp.route(
    "/<int:issue_id>/close",
    methods=["POST"],
)
@login_required
def close(issue_id):
    """
    Workflow:

        FINISH → CLOSE

    Requestor confirms that the issue has been solved.
    """

    updated_by = getattr(
        current_user,
        "username",
        None,
    )

    result = issue_service.close_issue(
        issue_id=issue_id,
        updated_by=updated_by,
    )

    if not result.success:

        flash(
            result.message,
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue_id,
            )
        )

    flash(
        result.message,
        "success",
    )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=issue_id,
        )
    )


# ==========================================================
# ISSUE STILL EXISTS
# ==========================================================

@issue_bp.route(
    "/<int:issue_id>/still-exists",
    methods=["POST"],
)
@login_required
def still_exists(issue_id):
    """
    Requestor says the issue still exists.

    Workflow:

        FINISH → IN_PROGRESS
    """

    updated_by = getattr(
        current_user,
        "username",
        None,
    )

    result = issue_service.reopen_issue(
        issue_id=issue_id,
        updated_by=updated_by,
    )

    if not result.success:

        flash(
            result.message,
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue_id,
            )
        )

    flash(
        result.message,
        "warning",
    )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=issue_id,
        )
    )


# ==========================================================
# DELETE
# ==========================================================

@issue_bp.route(
    "/<int:issue_id>/delete",
    methods=["POST"],
)
@login_required
def delete(issue_id):
    """
    Soft delete Issue.
    """

    issue = issue_service.get_by_id(
        issue_id
    )

    if not issue:

        flash(
            "Issue not found.",
            "danger",
        )

        return redirect(
            url_for("issue.index")
        )

    try:

        issue_service.repository.delete(
            issue
        )

        
        db.session.commit()

        flash(
            f"Issue {issue.issue_no} "
            "deleted successfully.",
            "success",
        )

    except Exception as exception:

        

        db.session.rollback()

        flash(
            f"Failed to delete Issue: "
            f"{str(exception)}",
            "danger",
        )

    return redirect(
        url_for("issue.index")
    )

# ==========================================================
# ADD ATTACHMENT
# ==========================================================

@issue_bp.route(
    "/<int:issue_id>/attachments/add",
    methods=["POST"],
)
@login_required
def add_attachment(issue_id):

    issue = issue_service.get_by_id(
        issue_id
    )

    if not issue:

        flash(
            "Issue not found.",
            "danger",
        )

        return redirect(
            url_for("issue.index")
        )

    # ------------------------------------------------------
    # Authorization
    # ------------------------------------------------------

    if not authorization_service.can_add_issue_attachment(
        user=current_user,
        issue=issue,
    ):

        flash(
            "You do not have permission to add attachment to this Issue.",
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue.id,
            )
        )

    # ------------------------------------------------------
    # File
    # ------------------------------------------------------

    file = request.files.get(
        "attachment"
    )

    # ------------------------------------------------------
    # Description
    # ------------------------------------------------------

    description = request.form.get(
        "description",
        "",
    ).strip()

    # ------------------------------------------------------
    # Created By
    # ------------------------------------------------------

    created_by = getattr(
        current_user,
        "username",
        None,
    )

    # ------------------------------------------------------
    # Add Attachment
    # ------------------------------------------------------

    result = issue_service.add_attachment(
        issue_id=issue_id,
        file=file,
        description=description,
        created_by=created_by,
    )

    if not result.success:

        flash(
            result.message,
            "danger",
        )

    else:

        flash(
            result.message,
            "success",
        )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=issue.id,
        )
    )

# ==========================================================
# DOWNLOAD ATTACHMENT
# ==========================================================

@issue_bp.route(
    "/attachments/<int:attachment_id>/download",
)
@login_required
def download_attachment(attachment_id):
    """
    Download Issue attachment.
    """

    attachment = issue_service.get_attachment(
        attachment_id
    )

    if not attachment:

        flash(
            "Attachment not found.",
            "danger",
        )

        return redirect(
            url_for("issue.index")
        )

    # ------------------------------------------------------
    # Get physical file path
    # ------------------------------------------------------

    file_path = Path(
        attachment.file_path
    )

    # ------------------------------------------------------
    # Convert relative path to absolute path
    # ------------------------------------------------------

    if not file_path.is_absolute():

        file_path = (
            Path.cwd()
            / file_path
        )

    file_path = file_path.resolve()

    # ------------------------------------------------------
    # Check physical file
    # ------------------------------------------------------

    if not file_path.exists():

        flash(
            f"Attachment file not found: "
            f"{attachment.file_name}",
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=attachment.issue_id,
            )
        )

    # ------------------------------------------------------
    # Download file
    # ------------------------------------------------------

    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=attachment.file_name,
    )

# ==========================================================
# PREVIEW ATTACHMENT
# ==========================================================

@issue_bp.route(
    "/attachments/<int:attachment_id>/preview",
)
@login_required
def preview_attachment(attachment_id):
    """
    Preview Issue attachment in browser.
    """

    attachment = issue_service.get_attachment(
        attachment_id
    )

    if not attachment:

        flash(
            "Attachment not found.",
            "danger",
        )

        return redirect(
            url_for("issue.index")
        )

    file_path = Path(
        attachment.file_path
    )

    # Convert to absolute path
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path

    file_path = file_path.resolve()

    # Check physical file
    if not file_path.exists():

        flash(
            f"Attachment file not found: "
            f"{attachment.file_name}",
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=attachment.issue_id,
            )
        )

    return send_file(
        str(file_path),
        as_attachment=False,
        download_name=attachment.file_name,
    )


# ==========================================================
# DELETE ATTACHMENT
# ==========================================================

@issue_bp.route(
    "/attachments/<int:attachment_id>/delete",
    methods=["POST"],
)
@login_required
def delete_attachment(attachment_id):

    attachment = issue_service.get_attachment(
        attachment_id
    )

    if not attachment:

        flash(
            "Attachment not found.",
            "danger",
        )

        return redirect(
            url_for("issue.index")
        )

    issue = issue_service.get_by_id(
        attachment.issue_id
    )

    if not issue:

        flash(
            "Issue not found.",
            "danger",
        )

        return redirect(
            url_for("issue.index")
        )

    # ------------------------------------------------------
    # Authorization
    # ------------------------------------------------------

    if not authorization_service.can_delete_issue_attachment(
        user=current_user,
        issue=issue,
    ):

        flash(
            "You do not have permission to delete this attachment.",
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue.id,
            )
        )

    # ------------------------------------------------------
    # Delete Attachment
    # ------------------------------------------------------

    result = issue_service.delete_attachment(
        attachment_id=attachment_id,
    )

    if not result.success:

        flash(
            result.message,
            "danger",
        )

    else:

        flash(
            result.message,
            "success",
        )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=issue.id,
        )
    )

@issue_bp.route(
    "/<int:issue_id>/clarification/create",
    methods=["POST"],
)
@login_required
def create_clarification(issue_id):
    """
    Admin creates a clarification request for an Issue.
    """

    issue = issue_service.get_by_id(issue_id)

    if not issue:
        flash("Issue not found.", "danger")
        return redirect(url_for("issue.index"))

    # ======================================================
    # Authorization
    # ======================================================

    if not authorization_service.can_request_issue_clarification(
        user=current_user,
        issue=issue,
    ):
        flash(
            "You do not have permission to request clarification.",
            "danger",
        )
        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue.id,
            )
        )

    # ======================================================
    # Validate Issue Status
    # ======================================================

    if issue.status != "IN_PROGRESS":
        flash(
            "Clarification can only be requested when the Issue is In Progress.",
            "warning",
        )
        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue.id,
            )
        )

    # ======================================================
    # Get Form Data
    # ======================================================

    question = request.form.get(
        "question",
        "",
    ).strip()

    if not question:
        flash(
            "Clarification question is required.",
            "danger",
        )
        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue.id,
            )
        )

    # ======================================================
    # Create Clarification
    # ======================================================

    clarification_service = IssueClarificationService()

    result = clarification_service.create_clarification(
        issue_id=issue.id,
        question=question,
        requested_by_employee_id=current_user.employee_id,
        created_by=getattr(
            current_user,
            "username",
            None,
        ),
    )

    if not result.success:
        flash(
            result.message,
            "danger",
        )
        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue.id,
            )
        )

    flash(
        result.message,
        "success",
    )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=issue.id,
        )
    )


@issue_bp.route(
    "/clarification/<int:clarification_id>/respond",
    methods=["POST"],
)
@login_required
def respond_clarification(clarification_id):

    clarification_service = IssueClarificationService()

    clarification = clarification_service.repository.get_by_id(
        clarification_id
    )

    if not clarification:
        flash(
            "Clarification not found.",
            "danger",
        )
        return redirect(
            url_for("issue.index")
        )

    issue = clarification.issue

    if not issue:
        flash(
            "Issue not found.",
            "danger",
        )
        return redirect(
            url_for("issue.index")
        )

    # ======================================================
    # Authorization
    # ======================================================

    if not authorization_service.can_respond_issue_clarification(
        user=current_user,
        clarification=clarification,
    ):
        flash(
            "You do not have permission to respond to this clarification.",
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue.id,
            )
        )

    # ======================================================
    # Response
    # ======================================================

    response = request.form.get(
        "response",
        "",
    ).strip()

    result = clarification_service.respond_clarification(
        clarification_id=clarification.id,
        response=response,
        responded_by_employee_id=current_user.employee_id,
        updated_by=getattr(
            current_user,
            "username",
            None,
        ),
    )

    if not result.success:
        flash(
            result.message,
            "danger",
        )

        return redirect(
            url_for(
                "issue.detail",
                issue_id=issue.id,
            )
        )

    flash(
        result.message,
        "success",
    )

    return redirect(
        url_for(
            "issue.detail",
            issue_id=issue.id,
        )
    )