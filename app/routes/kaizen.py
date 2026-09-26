from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_from_directory,
    abort,
    send_file
)

import os
import uuid

from werkzeug.utils import secure_filename

from flask_login import (
    login_required,
    current_user
)

from app.models.employee import Employee

from app.services.kaizen_service import (
    KaizenService
)

from app.services.kaizen_attachment_service import (
    KaizenAttachmentService
)

from app.repositories.kaizen_category_repository import (
    KaizenCategoryRepository
)

from app.repositories.department_repository import (
    DepartmentRepository
)
from app.services.problem_service import ProblemService
from app.services.authorization_service import (
    AuthorizationService,
)
from app.services.pdf_report_service import PDFReportService

# ==================================================
# Blueprint
# ==================================================

kaizen_bp = Blueprint(
    "kaizen",
    __name__,
    url_prefix="/kaizens"
)


# ==================================================
# Services / Repositories
# ==================================================

kaizen_service = KaizenService()
problem_service = ProblemService()
kaizen_category_repository = (
    KaizenCategoryRepository()
)

kaizen_attachment_service = (
    KaizenAttachmentService()
)

department_repository = (
    DepartmentRepository()
)
authorization_service = (
    AuthorizationService()
)


# ==================================================
# Attachment Configuration
# ==================================================

ALLOWED_KAIZEN_FILE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
}

MAX_KAIZEN_FILE_SIZE = 10 * 1024 * 1024


# ==========================================================
# Kaizen List
# ==========================================================

@kaizen_bp.route("/")
@login_required
def index():

    # ==================================================
    # Pagination
    # ==================================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int
    )

    if page < 1:
        page = 1

    if per_page < 1:
        per_page = 10


    # ==================================================
    # Search
    # ==================================================

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()


    # ==================================================
    # Status Filter
    # ==================================================

    status = request.args.get(
        "status",
        ""
    ).strip()


    # ==================================================
    # Department Filter
    # ==================================================

    department_id = request.args.get(
        "department_id",
        None,
        type=int
    )


    # ==================================================
    # Date Filter
    # ==================================================

    date_from = request.args.get(
        "date_from",
        ""
    ).strip()

    date_to = request.args.get(
        "date_to",
        ""
    ).strip()


    # ==================================================
    # MY KAIZEN
    # ==================================================

    mine = request.args.get(
        "mine",
        ""
    ).strip()

    employee_id = None

    if mine == "1":

        employee_id = current_user.employee_id


        # ==============================================
        # My Kaizen
        #
        # Default period:
        # Last 6 months
        # ==============================================

        from datetime import date

        from dateutil.relativedelta import relativedelta

        today = date.today()

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today


        if not date_from:

            date_from = (
                start_date.strftime(
                    "%Y-%m-%d"
                )
            )


        if not date_to:

            date_to = (
                end_date.strftime(
                    "%Y-%m-%d"
                )
            )


    # ==================================================
    # Sorting
    #
    # Default:
    # created_at DESC
    # ==================================================

    sort_by = request.args.get(
        "sort",
        "created_at"
    )

    sort_order = request.args.get(
        "order",
        "desc"
    )


    # ==================================================
    # Get Departments
    # ==================================================

    departments = (
        department_repository
        .get_all(
            is_active=True,
            page=1,
            per_page=1000,
            sort_by="department_name",
            sort_order="asc"
        )
    )


    # ==================================================
    # Get Kaizen
    # ==================================================

    result = kaizen_service.get_all(

        keyword=keyword,

        status=status,

        department_id=department_id,

        date_from=date_from,

        date_to=date_to,

        employee_id=employee_id,

        page=page,

        per_page=per_page,

        sort_by=sort_by,

        sort_order=sort_order
    )


    # ==================================================
    # Error
    # ==================================================

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return render_template(

            "kaizen/list.html",

            kaizens=None,

            keyword=keyword,

            status=status,

            department_id=department_id,

            date_from=date_from,

            date_to=date_to,

            departments=departments.items,

            sort_by=sort_by,

            sort_order=sort_order,

            mine=mine
        )


    # ==================================================
    # Data
    # ==================================================

    kaizens = result.data


    # ==================================================
    # Render
    # ==================================================

    return render_template(

        "kaizen/list.html",

        kaizens=kaizens,

        keyword=keyword,

        status=status,

        department_id=department_id,

        date_from=date_from,

        date_to=date_to,

        departments=departments.items,

        sort_by=sort_by,

        sort_order=sort_order,

        mine=mine
    )
# ==========================================================
# Select Problem for Create Kaizen
# ==========================================================


@kaizen_bp.route("/select-problem")
@login_required
def select_problem():

    # ======================================================
    # Request Parameters
    # ======================================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    sort_by = request.args.get(
        "sort",
        "problem_no"
    )

    sort_order = request.args.get(
        "order",
        "asc"
    )

    # ======================================================
    # Get Problems
    # ======================================================

    problems = problem_service.get_all(
        keyword=keyword,
        is_active=True,
        page=page,
        per_page=10,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # ======================================================
    # Render
    # ======================================================

    return render_template(
        "kaizen/select_problem.html",

        problems=problems,

        keyword=keyword,

        sort_by=sort_by,

        sort_order=sort_order
    )
# ==================================================
# Kaizen Detail
# ==================================================


@kaizen_bp.route(
    "/<int:kaizen_id>"
)
@login_required
def detail(kaizen_id):

    # ==================================================
    # Get Kaizen
    # ==================================================

    result = kaizen_service.get_by_id(
        kaizen_id
    )

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.index"
            )
        )

    kaizen = result.data


    # ==================================================
    # Current Employee
    # ==================================================

    current_employee = (
        Employee.query
        .filter_by(
            id=current_user.employee_id
        )
        .first()
    )


    # ==================================================
    # Authorization
    # ==================================================

    can_edit_kaizen = (
        authorization_service
        .can_edit_kaizen(
            user=current_user,
            kaizen=kaizen,
        )
    )


    can_approve_kaizen = (
        authorization_service
        .can_approve_kaizen(
            user=current_user,
            kaizen=kaizen,
        )
    )


    can_reject_kaizen = (
        authorization_service
        .can_reject_kaizen(
            user=current_user,
            kaizen=kaizen,
        )
    )


    # ==================================================
    # Render
    # ==================================================

    return render_template(

        "kaizen/detail.html",

        kaizen=kaizen,

        current_employee=(
            current_employee
        ),

        can_edit_kaizen=(
            can_edit_kaizen
        ),

        can_approve_kaizen=(
            can_approve_kaizen
        ),

        can_reject_kaizen=(
            can_reject_kaizen
        ),
    )

# ==================================================
# Create Kaizen from Improvement
# ==================================================

@kaizen_bp.route(
    "/improvement/<int:improvement_id>/create",
    methods=["GET", "POST"]
)
@login_required
def create(improvement_id):

    # ==================================================
    # Get Improvement
    # ==================================================

    improvement = (
        kaizen_service
        .improvement_repository
        .get_by_id(improvement_id)
    )

    if not improvement:

        flash(
            "Improvement not found.",
            "danger"
        )

        return redirect(
            url_for(
                "improvement.index"
            )
        )

    # ==================================================
    # Get Related Problem
    # ==================================================

    problem = improvement.problem

    if not problem:

        flash(
            "Related problem not found.",
            "danger"
        )

        return redirect(
            url_for(
                "improvement.detail",
                improvement_id=improvement_id
            )
        )

    # ==================================================
    # Get Current Employee
    # ==================================================

    current_employee = Employee.query.filter_by(
        id=current_user.employee_id
    ).first()

    if not current_employee:

        flash(
            "Logged-in user is not linked to an employee.",
            "danger"
        )

        return redirect(
            url_for(
                "improvement.detail",
                improvement_id=improvement_id
            )
        )

    # ==================================================
    # Get Kaizen Categories
    # ==================================================

    kaizen_categories = (
        kaizen_category_repository
        .get_all(
            is_active=True,
            page=1,
            per_page=100,
            sort_by="kaizen_category_name",
            sort_order="asc"
        )
    )

    # ==================================================
    # Get Departments
    # ==================================================

    departments = (
        department_repository
        .get_all(
            is_active=True,
            page=1,
            per_page=100,
            sort_by="department_name",
            sort_order="asc"
        )
    )

    # ==================================================
    # Create
    # ==================================================

    if request.method == "POST":

        try:

            result = kaizen_service.create(

                improvement_id=improvement_id,

                title=request.form.get(
                    "title"
                ),

                description=request.form.get(
                    "description"
                ),

                kaizen_category_id=request.form.get(
                    "kaizen_category_id",
                    type=int
                ),

                employee_id=current_user.employee_id,

                department_id=request.form.get(
                    "department_id",
                    type=int
                ),

                before_condition=request.form.get(
                    "before_condition"
                ),

                before_value=request.form.get(
                    "before_value",
                    type=float
                ),

                before_unit=request.form.get(
                    "before_unit"
                ),

                loss_before=request.form.get(
                    "loss_before"
                ),

                after_condition=request.form.get(
                    "after_condition"
                ),

                after_value=request.form.get(
                    "after_value",
                    type=float
                ),

                after_unit=request.form.get(
                    "after_unit"
                ),

                benefit=request.form.get(
                    "benefit"
                ),

                cost_saving=request.form.get(
                    "cost_saving",
                    type=float
                ),
                created_by=current_user.username,

                implementation_date=request.form.get(
                    "implementation_date"
                )
            )

            if not result.success:

                flash(
                    result.message,
                    "danger"
                )

            else:

                flash(
                    result.message,
                    "success"
                )

                return redirect(
                    url_for(
                        "kaizen.detail",
                        kaizen_id=result.data.id
                    )
                )

        except ValueError as e:

            flash(
                str(e),
                "danger"
            )

    # ==================================================
    # Form
    # ==================================================

    return render_template(
        "kaizen/form.html",

        mode="create",

        improvement=improvement,

        problem=problem,

        kaizen=None,
        employee=current_employee,

        current_employee=current_employee,

        kaizen_categories=(
            kaizen_categories.items
        ),

        departments=(
            departments.items
        )
    )


# ==================================================
# Edit Kaizen
# ==================================================
@kaizen_bp.route(
    "/<int:kaizen_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit(kaizen_id):

    # ==================================================
    # Get Kaizen
    # ==================================================

    result = kaizen_service.get_by_id(
        kaizen_id
    )

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.index"
            )
        )

    kaizen = result.data


    # ==================================================
    # Authorization
    #
    # ADMIN:
    #   Can edit all Kaizen
    #
    # USER:
    #   Can only edit his/her own Kaizen
    # ==================================================

    if not authorization_service.can_edit_kaizen(
        user=current_user,
        kaizen=kaizen,
    ):

        abort(403)


    # ==================================================
    # Status Authorization
    #
    # Only Draft and Rejected can be edited.
    # ==================================================

    if kaizen.status not in [
        "Draft",
        "Rejected"
    ]:

        flash(
            "This Kaizen cannot be edited "
            "because its current status is "
            f"'{kaizen.status}'.",
            "warning"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen.id
            )
        )


    # ==================================================
    # Get Current Employee
    # ==================================================

    current_employee = (
        Employee.query
        .filter_by(
            id=current_user.employee_id
        )
        .first()
    )


    # ==================================================
    # Get Kaizen Categories
    # ==================================================

    kaizen_categories = (
        kaizen_category_repository
        .get_all(
            is_active=True,
            page=1,
            per_page=100,
            sort_by="kaizen_category_name",
            sort_order="asc"
        )
    )


    # ==================================================
    # Get Departments
    # ==================================================

    departments = (
        department_repository
        .get_all(
            is_active=True,
            page=1,
            per_page=100,
            sort_by="department_name",
            sort_order="asc"
        )
    )


    # ==================================================
    # Edit
    # ==================================================

    if request.method == "POST":

        try:

            result = kaizen_service.update(

                kaizen_id=kaizen_id,

                title=request.form.get(
                    "title"
                ),

                description=request.form.get(
                    "description"
                ),

                kaizen_category_id=request.form.get(
                    "kaizen_category_id",
                    type=int
                ),

                department_id=request.form.get(
                    "department_id",
                    type=int
                ),

                before_condition=request.form.get(
                    "before_condition"
                ),

                before_value=request.form.get(
                    "before_value",
                    type=float
                ),

                before_unit=request.form.get(
                    "before_unit"
                ),

                loss_before=request.form.get(
                    "loss_before"
                ),

                after_condition=request.form.get(
                    "after_condition"
                ),

                after_value=request.form.get(
                    "after_value",
                    type=float
                ),

                after_unit=request.form.get(
                    "after_unit"
                ),

                benefit=request.form.get(
                    "benefit"
                ),

                cost_saving=request.form.get(
                    "cost_saving",
                    type=float
                ),

                implementation_date=request.form.get(
                    "implementation_date"
                )
            )


            # ==========================================
            # Update Failed
            # ==========================================

            if not result.success:

                flash(
                    result.message,
                    "danger"
                )

            else:

                flash(
                    result.message,
                    "success"
                )

                return redirect(
                    url_for(
                        "kaizen.detail",
                        kaizen_id=kaizen_id
                    )
                )


        except ValueError as e:

            flash(
                str(e),
                "danger"
            )


    # ==================================================
    # Form
    # ==================================================

    return render_template(
        "kaizen/form.html",

        mode="edit",

        kaizen=kaizen,

        current_employee=current_employee,

        kaizen_categories=(
            kaizen_categories.items
        ),

        departments=(
            departments.items
        ),

        improvement=kaizen.improvement,

        problem=(
            kaizen.improvement.problem
            if kaizen.improvement
            else None
        )
    )

# ==================================================
# Submit Proposal
# ==================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/submit",
    methods=["POST"]
)
@login_required
def submit(kaizen_id):

    result = kaizen_service.submit_proposal(
        kaizen_id
    )

    if result.success:

        flash(
            result.message,
            "success"
        )

    else:

        flash(
            result.message,
            "danger"
        )

    return redirect(
        url_for(
            "kaizen.detail",
            kaizen_id=kaizen_id
        )
    )


# ==========================================================
# Approval
# ==========================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/approve",
    methods=["POST"]
)
@login_required
def approve(kaizen_id):

    # ==================================================
    # Get Kaizen
    # ==================================================

    result = kaizen_service.get_by_id(
        kaizen_id
    )

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.index"
            )
        )

    kaizen = result.data


    # ==================================================
    # Authorization
    #
    # ADMIN:
    #   Can approve all Kaizen
    #
    # USER:
    #   Must have KAIZEN_APPROVE permission
    #   and Approval Authority for the
    #   Kaizen department.
    # ==================================================

    if not authorization_service.can_approve_kaizen(
        user=current_user,
        kaizen=kaizen,
    ):

        abort(403)


    # ==================================================
    # Validate Employee
    # ==================================================

    approved_by_employee_id = (
        current_user.employee_id
    )

    if not approved_by_employee_id:

        flash(
            "Logged-in user is not linked to an employee.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )


    # ==================================================
    # Approve
    # ==================================================

    result = kaizen_service.approve(

        kaizen_id=kaizen_id,

        employee_id=approved_by_employee_id
    )


    # ==================================================
    # Result
    # ==================================================

    if result.success:

        flash(
            result.message,
            "success"
        )

    else:

        flash(
            result.message,
            "danger"
        )


    # ==================================================
    # Return
    # ==================================================

    return redirect(
        url_for(
            "kaizen.detail",
            kaizen_id=kaizen_id
        )
    )


# ==========================================================
# Rejection
# ==========================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/reject",
    methods=["POST"]
)
@login_required
def reject(kaizen_id):

    # ==================================================
    # Get Kaizen
    # ==================================================

    result = kaizen_service.get_by_id(
        kaizen_id
    )

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.index"
            )
        )

    kaizen = result.data


    # ==================================================
    # Authorization
    #
    # ADMIN:
    #   Can reject all Kaizen
    #
    # USER:
    #   Must have KAIZEN_APPROVE permission
    #   and Approval Authority for the
    #   Kaizen department.
    # ==================================================

    if not authorization_service.can_reject_kaizen(
        user=current_user,
        kaizen=kaizen,
    ):

        abort(403)


    # ==================================================
    # Validate Employee
    # ==================================================

    rejected_by_employee_id = (
        current_user.employee_id
    )

    if not rejected_by_employee_id:

        flash(
            "Logged-in user is not linked to an employee.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )


    # ==================================================
    # Rejection Reason
    # ==================================================

    rejection_reason = (
        request.form.get(
            "rejection_reason",
            ""
        ).strip()
    )


    if not rejection_reason:

        flash(
            "Rejection reason is required.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )


    # ==================================================
    # Reject
    # ==================================================

    result = kaizen_service.reject(

        kaizen_id=kaizen_id,

        employee_id=rejected_by_employee_id,

        rejection_reason=rejection_reason
    )


    # ==================================================
    # Result
    # ==================================================

    if result.success:

        flash(
            result.message,
            "success"
        )

    else:

        flash(
            result.message,
            "danger"
        )


    # ==================================================
    # Return
    # ==================================================

    return redirect(
        url_for(
            "kaizen.detail",
            kaizen_id=kaizen_id
        )
    )

# ==================================================
# Implementation
# ==================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/implementation",
    methods=["GET", "POST"]
)
@login_required
def implementation(kaizen_id):

    result = kaizen_service.get_by_id(
        kaizen_id
    )

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for("kaizen.index")
        )

    kaizen = result.data

    if request.method == "POST":

        try:

            result = kaizen_service.mark_implemented(
                kaizen_id
            )

            if not result.success:

                flash(
                    result.message,
                    "danger"
                )

            else:

                flash(
                    result.message,
                    "success"
                )

                return redirect(
                    url_for(
                        "kaizen.detail",
                        kaizen_id=kaizen_id
                    )
                )

        except ValueError as e:

            flash(
                str(e),
                "danger"
            )

    return render_template(
        "kaizen/implementation.html",
        kaizen=kaizen
    )


# ==================================================
# Delete Kaizen
# ==================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/delete",
    methods=["POST"]
)
@login_required
def delete(kaizen_id):

    result = kaizen_service.delete(
        kaizen_id
    )

    if result.success:

        flash(
            result.message,
            "success"
        )

        return redirect(
            url_for("kaizen.index")
        )

    flash(
        result.message,
        "danger"
    )

    return redirect(
        url_for(
            "kaizen.detail",
            kaizen_id=kaizen_id
        )
    )


# ==================================================
# Select Improvement for Kaizen
# ==================================================

@kaizen_bp.route(
    "/select-improvement"
)
@login_required
def select_improvement():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    result = (
        kaizen_service
        .improvement_repository
        .get_all(
            keyword=keyword,
            page=page,
            per_page=10,
            sort_by="improvement_no",
            sort_order="asc"
        )
    )

    return render_template(
        "kaizen/select_improvement.html",
        improvements=result,
        keyword=keyword
    )


# ==================================================
# Upload Kaizen Attachment
# ==================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/attachments",
    methods=["POST"]
)
@login_required
def upload_attachment(kaizen_id):

    # ==================================================
    # Check Kaizen
    # ==================================================

    result = kaizen_service.get_by_id(
        kaizen_id
    )

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for("kaizen.index")
        )

    # ==================================================
    # Get File
    # ==================================================

    file = request.files.get(
        "file"
    )

    attachment_type = request.form.get(
        "attachment_type",
        "GENERAL"
    ).strip().upper()

    description = request.form.get(
        "description"
    )

    # ==================================================
    # Validate Attachment Type
    # ==================================================

    if attachment_type not in {
        "BEFORE",
        "AFTER",
        "GENERAL"
    }:

        flash(
            "Invalid attachment type.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    # ==================================================
    # Validate File
    # ==================================================

    if not file or not file.filename:

        flash(
            "Please select a file.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    original_filename = secure_filename(
        file.filename
    )

    if not original_filename:

        flash(
            "Invalid file name.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    # ==================================================
    # Extension
    # ==================================================

    if "." not in original_filename:

        flash(
            "File extension is required.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    extension = (
        original_filename
        .rsplit(".", 1)[1]
        .lower()
    )

    if extension not in ALLOWED_KAIZEN_FILE_EXTENSIONS:

        flash(
            f"File type '.{extension}' is not allowed.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    # ==================================================
    # File Size
    # ==================================================

    file.seek(
        0,
        os.SEEK_END
    )

    file_size = file.tell()

    file.seek(0)

    if file_size > MAX_KAIZEN_FILE_SIZE:

        flash(
            "Maximum file size is 10 MB.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    # ==================================================
    # Upload Folder
    # ==================================================

    upload_folder = os.path.join(

        current_app.root_path,

        "static",

        "uploads",

        "kaizen",

        attachment_type
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    # ==================================================
    # Generate Stored Name
    # ==================================================

    stored_name = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    file_path = os.path.join(
        upload_folder,
        stored_name
    )

    # ==================================================
    # Save Physical File
    # ==================================================

    try:

        file.save(
            file_path
        )

        relative_path = os.path.join(
            "uploads",
            "kaizen",
            attachment_type,
            stored_name
        ).replace(
            "\\",
            "/"
        )

        # ==================================================
        # Save Attachment Record
        # ==================================================

        result = kaizen_attachment_service.create(

            kaizen_id=kaizen_id,

            file_name=original_filename,

            stored_name=stored_name,

            file_path=relative_path,

            file_type=extension,

            file_size=file_size,

            description=description,

            attachment_type=attachment_type
        )

        if not result.success:

            if os.path.exists(file_path):

                os.remove(file_path)

            flash(
                result.message,
                "danger"
            )

            return redirect(
                url_for(
                    "kaizen.detail",
                    kaizen_id=kaizen_id
                )
            )

        flash(
            result.message,
            "success"
        )

    except Exception as exception:

        if os.path.exists(file_path):

            os.remove(file_path)

        current_app.logger.exception(
            "Failed to upload Kaizen attachment."
        )

        flash(
            f"Failed to upload attachment: {str(exception)}",
            "danger"
        )

    return redirect(
        url_for(
            "kaizen.detail",
            kaizen_id=kaizen_id
        )
    )


# ==================================================
# Preview Attachment
# ==================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/attachments/<int:attachment_id>/preview"
)
@login_required
def preview_attachment(
    kaizen_id,
    attachment_id
):

    result = (
        kaizen_attachment_service
        .get_by_id_and_kaizen(
            attachment_id,
            kaizen_id
        )
    )

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    attachment = result.data

    full_path = os.path.join(
        current_app.root_path,
        "static",
        attachment.file_path
    )

    if not os.path.isfile(full_path):

        flash(
            "Attachment file not found.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    directory = os.path.dirname(
        full_path
    )

    return send_from_directory(
        directory,
        os.path.basename(full_path),
        as_attachment=False
    )


# ==================================================
# Download Attachment
# ==================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/attachments/<int:attachment_id>/download"
)
@login_required
def download_attachment(
    kaizen_id,
    attachment_id
):

    result = (
        kaizen_attachment_service
        .get_by_id_and_kaizen(
            attachment_id,
            kaizen_id
        )
    )

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    attachment = result.data

    full_path = os.path.join(
        current_app.root_path,
        "static",
        attachment.file_path
    )

    if not os.path.isfile(full_path):

        flash(
            "Attachment file not found.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    directory = os.path.dirname(
        full_path
    )

    return send_from_directory(

        directory,

        os.path.basename(full_path),

        as_attachment=True,

        download_name=attachment.file_name
    )


# ==================================================
# Delete Attachment
# ==================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/attachments/<int:attachment_id>/delete",
    methods=["POST"]
)
@login_required
def delete_attachment(
    kaizen_id,
    attachment_id
):

    result = (
        kaizen_attachment_service
        .get_by_id_and_kaizen(
            attachment_id,
            kaizen_id
        )
    )

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    attachment = result.data

    # ==================================================
    # Physical File
    # ==================================================

    full_path = os.path.join(
        current_app.root_path,
        "static",
        attachment.file_path
    )

    # ==================================================
    # Delete DB Record
    # ==================================================

    delete_result = (
        kaizen_attachment_service.delete(
            attachment_id,
            kaizen_id
        )
    )

    if not delete_result.success:

        flash(
            delete_result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    # ==================================================
    # Delete Physical File
    # ==================================================

    try:

        if os.path.isfile(full_path):

            os.remove(
                full_path
            )

    except Exception:

        current_app.logger.exception(
            "Failed to delete physical Kaizen attachment."
        )

    flash(
        delete_result.message,
        "success"
    )

    return redirect(
        url_for(
            "kaizen.detail",
            kaizen_id=kaizen_id
        )
    )


# ==================================================
# Update Attachment Description
# ==================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/attachments/<int:attachment_id>/description",
    methods=["POST"]
)
@login_required
def update_attachment_description(
    kaizen_id,
    attachment_id
):

    description = request.form.get(
        "description"
    )

    result = (
        kaizen_attachment_service
        .update_description(
            attachment_id=attachment_id,
            kaizen_id=kaizen_id,
            description=description
        )
    )

    if result.success:

        flash(
            result.message,
            "success"
        )

    else:

        flash(
            result.message,
            "danger"
        )

    return redirect(
        url_for(
            "kaizen.detail",
            kaizen_id=kaizen_id
        )
    )

# ==========================================================
# Create Kaizen from Problem
# ==========================================================

@kaizen_bp.route(
    "/problem/<int:problem_id>/create",
    methods=["GET", "POST"]
)
@login_required
def create_from_problem(problem_id):

    # ======================================================
    # Get Problem
    # ======================================================

    problem = problem_service.get_by_id(
        problem_id
    )

    if not problem:

        flash(
            "Problem not found.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.select_problem"
            )
        )


    # ======================================================
    # Get Current Employee
    # ======================================================

    current_employee = Employee.query.filter_by(
        id=current_user.employee_id
    ).first()

    if not current_employee:

        flash(
            "Current user is not linked to an employee.",
            "danger"
        )

        return redirect(
            url_for("kaizen.select_problem")
        )

    if not current_employee:

        flash(
            "Logged-in user is not linked to an employee.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.select_problem"
            )
        )

    # ======================================================
    # Get Kaizen Categories
    # ======================================================

    kaizen_categories = (
        kaizen_category_repository
        .get_all(
            is_active=True,
            page=1,
            per_page=100,
            sort_by="kaizen_category_name",
            sort_order="asc"
        )
    )

    # ======================================================
    # Get Departments
    # ======================================================

    departments = (
        department_repository
        .get_all(
            is_active=True,
            page=1,
            per_page=100,
            sort_by="department_name",
            sort_order="asc"
        )
    )

    # ======================================================
    # CREATE
    # ======================================================

    if request.method == "POST":

        try:

            result = kaizen_service.create_from_problem(

                problem_id=problem_id,

                title=request.form.get(
                    "title"
                ),

                description=request.form.get(
                    "description"
                ),

                kaizen_category_id=request.form.get(
                    "kaizen_category_id",
                    type=int
                ),

                employee_id=current_user.employee_id,

                department_id=request.form.get(
                    "department_id",
                    type=int
                ),

                before_condition=request.form.get(
                    "before_condition"
                ),

                before_value=request.form.get(
                    "before_value",
                    type=float
                ),

                before_unit=request.form.get(
                    "before_unit"
                ),

                loss_before=request.form.get(
                    "loss_before"
                ),

                after_condition=request.form.get(
                    "after_condition"
                ),

                after_value=request.form.get(
                    "after_value",
                    type=float
                ),

                after_unit=request.form.get(
                    "after_unit"
                ),

                benefit=request.form.get(
                    "benefit"
                ),

                cost_saving=request.form.get(
                    "cost_saving",
                    type=float
                ),

                implementation_date=request.form.get(
                    "implementation_date"
                )
            )

            # ==================================================
            # Result
            # ==================================================

            if not result.success:

                flash(
                    result.message,
                    "danger"
                )

            else:

                flash(
                    result.message,
                    "success"
                )

                return redirect(
                    url_for(
                        "kaizen.detail",
                        kaizen_id=result.data.id
                    )
                )

        except ValueError as exception:

            flash(
                str(exception),
                "danger"
            )

    # ======================================================
    # Form
    # ======================================================

    return render_template(

        "kaizen/form.html",

        mode="create",

        source="problem",

        kaizen=None,

        improvement=None,

        problem=problem,

        employee=current_employee,
        
        current_employee=current_employee,

        kaizen_categories=(
            kaizen_categories.items
        ),

        departments=(
            departments.items
        )
    )


# ==========================================================
# Create Kaizen Directly
# ==========================================================

@kaizen_bp.route(
    "/create-direct",
    methods=["GET", "POST"]
)
@login_required
def create_direct():

    # ======================================================
    # Get Current Employee
    # ======================================================

    current_employee = Employee.query.filter_by(
        id=current_user.employee_id
    ).first()

    if not current_employee:

        flash(
            "Current user is not linked to an employee.",
            "danger"
        )

        return redirect(
            url_for("kaizen.index")
        )

    # ======================================================
    # Get Kaizen Categories
    # ======================================================

    kaizen_categories = (
        kaizen_category_repository
        .get_all(
            is_active=True,
            page=1,
            per_page=100,
            sort_by="kaizen_category_name",
            sort_order="asc"
        )
    )

    # ======================================================
    # Get Departments
    # ======================================================

    departments = (
        department_repository
        .get_all(
            is_active=True,
            page=1,
            per_page=100,
            sort_by="department_name",
            sort_order="asc"
        )
    )

    # ======================================================
    # POST
    # ======================================================

    if request.method == "POST":

        try:

            result = kaizen_service.create_direct(

                title=request.form.get(
                    "title"
                ),

                description=request.form.get(
                    "description"
                ),

                kaizen_category_id=request.form.get(
                    "kaizen_category_id",
                    type=int
                ),

                employee_id=current_user.employee_id,

                department_id=request.form.get(
                    "department_id",
                    type=int
                ),

                before_condition=request.form.get(
                    "before_condition"
                ),

                before_value=request.form.get(
                    "before_value",
                    type=float
                ),

                before_unit=request.form.get(
                    "before_unit"
                ),

                loss_before=request.form.get(
                    "loss_before"
                ),

                after_condition=request.form.get(
                    "after_condition"
                ),

                after_value=request.form.get(
                    "after_value",
                    type=float
                ),

                after_unit=request.form.get(
                    "after_unit"
                ),

                benefit=request.form.get(
                    "benefit"
                ),

                cost_saving=request.form.get(
                    "cost_saving",
                    type=float
                ),

                implementation_date=request.form.get(
                    "implementation_date"
                )
            )

            # ==================================================
            # Result
            # ==================================================

            if not result.success:

                flash(
                    result.message,
                    "danger"
                )

            else:

                flash(
                    result.message,
                    "success"
                )

                return redirect(
                    url_for(
                        "kaizen.detail",
                        kaizen_id=result.data.id
                    )
                )

        except ValueError as exception:

            flash(
                str(exception),
                "danger"
            )

    # ======================================================
    # Render Form
    # ======================================================

    return render_template(

        "kaizen/form.html",

        mode="create",

        source="direct",

        kaizen=None,

        improvement=None,

        problem=None,
        employee=current_employee,

        current_employee=current_employee,

        kaizen_categories=(
            kaizen_categories.items
        ),

        departments=(
            departments.items
        )
    )



# =========================================================
# EXPORT KAIZEN PDF
# =========================================================

@kaizen_bp.route(
    "/<int:kaizen_id>/export-pdf"
)
@login_required
def export_pdf(kaizen_id):

    # -----------------------------------------------------
    # Get Kaizen
    # -----------------------------------------------------

    result = kaizen_service.get_by_id(
        kaizen_id
    )

    # -----------------------------------------------------
    # Kaizen not found
    # -----------------------------------------------------

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.index"
            )
        )

    # -----------------------------------------------------
    # Get Kaizen Data
    # -----------------------------------------------------

    kaizen = result.data

    # -----------------------------------------------------
    # Get Current Employee
    # -----------------------------------------------------

    current_employee = (
        Employee.query
        .filter_by(
            id=current_user.employee_id
        )
        .first()
    )

    # -----------------------------------------------------
    # Printed By
    # -----------------------------------------------------

    printed_by = None

    if current_employee:

        printed_by = (
            getattr(
                current_employee,
                "full_name",
                None
            )
            or getattr(
                current_employee,
                "name",
                None
            )
        )

    # Fallback to username
    if not printed_by:

        printed_by = getattr(
            current_user,
            "username",
            None
        )

    # -----------------------------------------------------
    # Generate PDF
    # -----------------------------------------------------

    try:

        pdf_file = (
            PDFReportService
            .generate_kaizen_report(
                kaizen=kaizen,
                printed_by=printed_by
            )
        )

    except Exception:

        current_app.logger.exception(
            "Failed to generate Kaizen PDF "
            "for Kaizen ID %s",
            kaizen_id
        )

        flash(
            "Failed to generate Kaizen PDF.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen.detail",
                kaizen_id=kaizen_id
            )
        )

    # -----------------------------------------------------
    # Return PDF
    # -----------------------------------------------------

    return send_file(

        pdf_file,

        mimetype="application/pdf",

        as_attachment=False,

        download_name=(
            f"Kaizen_Report_"
            f"{kaizen.kaizen_no}.pdf"
        )
    )