from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    send_file,
)
from datetime import date

from dateutil.relativedelta import relativedelta
from flask_login import (
    login_required,
    current_user,
)

from app.models.employee import Employee

from app.services import problem_service

from app.services.improvement_service import (
    ImprovementService,
)

from app.core.choices.problem import (
    PROBLEM_STATUS,
    ProblemStatus,
)

from app.services.authorization_service import (
    AuthorizationService,
)
from app.repositories.improvement_pic_repository import (
    ImprovementPICRepository,
)
from app.services.department_service import DepartmentService
from app.services.pdf_report_service import (
    PDFReportService,
)

# ==========================================================
# Blueprint
# ==========================================================

improvement_bp = Blueprint(
    "improvement",
    __name__,
    url_prefix="/improvements",
)


# ==========================================================
# Services
# ==========================================================

improvement_service = ImprovementService()

problem_service = (
    problem_service.ProblemService()
)

authorization_service = (
    AuthorizationService()
)

improvement_pic_repository = (
    ImprovementPICRepository()
)
department_service = DepartmentService()


# ==========================================================
# Improvement List
# ==========================================================

# ==========================================================
# Improvement List
# ==========================================================

@improvement_bp.route("/")
@login_required
def index():

    # ==================================================
    # Pagination
    # ==================================================

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

    # Prevent invalid pagination values
    if page < 1:
        page = 1

    if per_page < 1:
        per_page = 10

    # ==================================================
    # Search
    # ==================================================

    keyword = request.args.get(
        "keyword",
        "",
    ).strip()

    # ==================================================
    # My Improvement Filter
    # ==================================================

    mine = request.args.get(
        "mine",
        "",
    ).strip()

    created_by = None

    if mine == "1":
        created_by = current_user.employee_id

    # ==================================================
    # Approval Filter
    # ==================================================

    approval = request.args.get(
        "approval",
        "",
    ).strip()

    # ==================================================
    # Sorting
    # ==================================================

    sort_order = request.args.get(
        "order",
        "desc",
    )

    sort_by = request.args.get(
        "sort",
        "id",
    )

    # ==================================================
    # Date Filter
    # ==================================================

    date_from = request.args.get(
        "date_from",
        "",
    ).strip()

    date_to = request.args.get(
        "date_to",
        "",
    ).strip()

    # ==================================================
    # My Improvement = Last 6 Months
    #
    # Harus sama dengan UserDashboardService
    # ==================================================

    if mine == "1":

        today = date.today()

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today

        # Hanya gunakan periode default 6 bulan
        # apabila user tidak memilih filter tanggal.
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
    # Get Improvements
    # ==================================================
 
    improvements = improvement_service.get_all(
        keyword=keyword,
        approval=approval,
        date_from=date_from,
        date_to=date_to,
        created_by=created_by,
        page=page,
        per_page=per_page,
        sort_order=sort_order,
        sort_by=sort_by,
    )



    # ==================================================
    # Render
    # ==================================================

    return render_template(
        "improvement/list.html",

        improvements=improvements,

        keyword=keyword,

        approval=approval,

        date_from=date_from,

        date_to=date_to,

        sort_order=sort_order,

        sort_by=sort_by,

        per_page=per_page,

        mine=mine,
    )
# ==========================================================
# Select Problem for Improvement
# ==========================================================

@improvement_bp.route(
    "/select-problem"
)
@login_required
def select_problem():

    # ==================================================
    # Pagination
    # ==================================================

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

    # Prevent invalid pagination values
    if page < 1:
        page = 1

    if per_page < 1:
        per_page = 10

    # ==================================================
    # Search
    # ==================================================

    keyword = request.args.get(
        "keyword",
        "",
    ).strip()

    # ==================================================
    # Status Filter
    # ==================================================

    status = request.args.get(
        "status",
        "",
    ).strip()

    # ==================================================
    # Department Filter
    # ==================================================

    department_id = request.args.get(
        "department_id",
        None,
        type=int,
    )

    # ==================================================
    # Get Departments
    # ==================================================

    departments = department_service.get_all(
        page=1,
        per_page=1000,
        sort_by="department_name",
        sort_order="asc",
    )

    # ==================================================
    # Get Problems
    # ==================================================

    result = problem_service.get_all(
        keyword=keyword,
        status=status,
        priority="",
        department_id=department_id,
        page=page,
        per_page=per_page,
        sort_by="problem_no",
        sort_order="asc",
    )

    # ==================================================
    # Render
    # ==================================================

    return render_template(
        "improvement/problem_list.html",

        problems=result,

        keyword=keyword,

        status=status,

        department_id=department_id,

        departments=departments.items,

        PROBLEM_STATUS=ProblemStatus,
    )


# ==========================================================
# Improvement Detail
# ==========================================================

@improvement_bp.route(
    "/<int:improvement_id>"
)
@login_required
def detail(improvement_id):

    # ==================================================
    # Get Improvement
    # ==================================================

    improvement = (
        improvement_service.get_by_id(
            improvement_id
        )
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
    # Calculate Benefit
    # ==================================================

    benefit = (
        improvement_service.calculate_benefit(
            improvement_id
        )
    )

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
    # Get Improvement PIC
    # ==================================================

    improvement_pics = (
        improvement_pic_repository
        .find_by_improvement_id(
            improvement_id=improvement_id,
            active_only=False,
        )
    )

    # ==================================================
    # Authorization
    # ==================================================

    can_edit_improvement = (
        authorization_service
        .can_edit_improvement(
            user=current_user,
            improvement=improvement,
        )
    )

    can_assign_improvement = (
        authorization_service
        .can_assign_improvement(
            user=current_user,
            improvement=improvement,
        )
    )

    can_approve_improvement = (
        authorization_service
        .can_approve_improvement(
            user=current_user,
            improvement=improvement,
        )
    )

    print("==========================================")
    print("APPROVAL DEBUG")

    print(
        "Username       :",
        current_user.username
    )

    print(
        "Role Code      :",
        current_user.role_code
    )

    print(
        "Is Admin       :",
        authorization_service._is_admin(
            current_user
        )
    )

    print(
        "Employee ID    :",
        current_user.employee_id
    )

    print(
        "Permission     :",
        current_user.has_permission(
            "IMPROVEMENT_APPROVE"
        )
    )

    print(
        "Problem Dept   :",
        improvement.problem.department_id
    )

    print(
        "Verification   :",
        improvement.verification_result
    )

    print(
        "Approved Date  :",
        improvement.approved_date
    )

    print(
        "Can Approve    :",
        can_approve_improvement
    )


    print("==========================================")


    can_update_implementation_result = (
        authorization_service
        .can_update_implementation_result(
            user=current_user,
            improvement=improvement,
        )
    )

    can_verify_improvement = (
        authorization_service
        .can_verify_improvement(
            user=current_user,
            improvement=improvement,
        )
    )

    # ==================================================
    # Render
    # ==================================================

    return render_template(

        "improvement/detail.html",

        improvement=improvement,

        benefit=benefit,

        current_employee=(
            current_employee
        ),

        improvement_pics=(
            improvement_pics
        ),

        can_edit_improvement=(
            can_edit_improvement
        ),

        can_assign_improvement=(
            can_assign_improvement
        ),

        can_approve_improvement=(
            can_approve_improvement
        ),

        can_update_implementation_result=(
            can_update_implementation_result
        ),

        can_verify_improvement=(
            can_verify_improvement
        ),
    )

# ==========================================================
# Create Improvement
# ==========================================================

@improvement_bp.route(
    "/problem/<int:problem_id>/create",
    methods=["GET", "POST"],
)
@login_required
def create(problem_id):

    # ==================================================
    # Get Problem
    # ==================================================

    problem = (
        improvement_service
        .problem_repository
        .get_by_id(
            problem_id
        )
    )

    if not problem:

        flash(
            "Problem not found.",
            "danger",
        )

        return redirect(
            url_for(
                "problem.index"
            )
        )

    # ==================================================
    # Create
    # ==================================================

    if request.method == "POST":

        try:

            improvement = (
                improvement_service
                .create_improvement(
                    problem_id=problem_id,
                    title=request.form.get(
                        "title"
                    ),
                    description=request.form.get(
                        "description"
                    ),
                    created_by_employee_id=(
                        current_user.employee_id
                    ),
                    root_cause=request.form.get(
                        "root_cause"
                    ),
                    improvement_plan=request.form.get(
                        "improvement_plan"
                    ),
                    improvement_cost=request.form.get(
                        "improvement_cost",
                        0,
                    ),
                    estimated_time_saving=(
                        request.form.get(
                            "estimated_time_saving",
                            0,
                        )
                    ),
                    estimated_cost_saving=(
                        request.form.get(
                            "estimated_cost_saving",
                            0,
                        )
                    ),
                    estimated_benefit=(
                        request.form.get(
                            "estimated_benefit",
                            0,
                        )
                    ),
                )
            )

            flash(
                "Improvement created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "improvement.detail",
                    improvement_id=(
                        improvement.id
                    ),
                )
            )

        except ValueError as e:

            flash(
                str(e),
                "danger",
            )

    # ==================================================
    # Form
    # ==================================================

    return render_template(
        "improvement/form.html",
        mode="create",
        problem=problem,
        improvement=None,
    )


# ==========================================================
# Edit Improvement
# ==========================================================

@improvement_bp.route(
    "/<int:improvement_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(improvement_id):

    # ==================================================
    # Get Improvement
    # ==================================================

    improvement = (
        improvement_service.get_by_id(
            improvement_id
        )
    )

    if not improvement:

        flash(
            "Improvement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "improvement.index"
            )
        )

    # ==================================================
    # Authorization
    # ==================================================

    if not authorization_service.can_edit_improvement(
        user=current_user,
        improvement=improvement,
    ):

        abort(403)

    # ==================================================
    # Get Problem
    # ==================================================

    problem = improvement.problem

    if not problem:

        flash(
            "Related problem not found.",
            "danger",
        )

        return redirect(
            url_for(
                "improvement.index"
            )
        )

    # ==================================================
    # Edit
    # ==================================================

    if request.method == "POST":

        try:

            improvement_service.update_improvement(
                improvement_id=improvement_id,
                title=request.form.get(
                    "title"
                ),
                description=request.form.get(
                    "description"
                ),
                root_cause=request.form.get(
                    "root_cause"
                ),
                improvement_plan=request.form.get(
                    "improvement_plan"
                ),
                improvement_cost=request.form.get(
                    "improvement_cost",
                    0,
                ),
                estimated_time_saving=(
                    request.form.get(
                        "estimated_time_saving",
                        0,
                    )
                ),
                estimated_cost_saving=(
                    request.form.get(
                        "estimated_cost_saving",
                        0,
                    )
                ),
                estimated_benefit=(
                    request.form.get(
                        "estimated_benefit",
                        0,
                    )
                ),
            )

            flash(
                "Improvement updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "improvement.detail",
                    improvement_id=(
                        improvement.id
                    ),
                )
            )

        except ValueError as e:

            flash(
                str(e),
                "danger",
            )

    # ==================================================
    # Form
    # ==================================================

    return render_template(
        "improvement/form.html",
        mode="edit",
        problem=problem,
        improvement=improvement,
    )


# ==========================================================
# Implementation
# ==========================================================

@improvement_bp.route(
    "/<int:improvement_id>/implementation",
    methods=["GET", "POST"],
)
@login_required
def implementation(improvement_id):

    # ==================================================
    # Get Improvement
    # ==================================================

    improvement = (
        improvement_service.get_by_id(
            improvement_id
        )
    )

    if not improvement:

        flash(
            "Improvement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "improvement.index"
            )
        )

    # ==================================================
    # Update Implementation
    # ==================================================

    if request.method == "POST":

        try:

            improvement_service.update_implementation(
                improvement_id=improvement_id,
                implementation_result=request.form[
                    "implementation_result"
                ],
            )

            flash(
                "Implementation result updated.",
                "success",
            )

            return redirect(
                url_for(
                    "improvement.detail",
                    improvement_id=(
                        improvement_id
                    ),
                )
            )

        except ValueError as e:

            flash(
                str(e),
                "danger",
            )

    # ==================================================
    # Render
    # ==================================================

    return render_template(
        "improvement/implementation.html",
        improvement=improvement,
    )


# ==========================================================
# Verification
# ==========================================================

@improvement_bp.route(
    "/<int:improvement_id>/verification",
    methods=["GET", "POST"],
)
@login_required
def verification(improvement_id):

    # ==================================================
    # Get Improvement
    # ==================================================

    improvement = (
        improvement_service.get_by_id(
            improvement_id
        )
    )

    if not improvement:

        flash(
            "Improvement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "improvement.index"
            )
        )

    # ==================================================
    # Verification
    # ==================================================

    if request.method == "POST":

        try:

            improvement_service.verify_improvement(
                improvement_id=improvement_id,
                verification_result=request.form[
                    "verification_result"
                ],
            )

            flash(
                "Improvement verified successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "improvement.detail",
                    improvement_id=(
                        improvement_id
                    ),
                )
            )

        except ValueError as e:

            flash(
                str(e),
                "danger",
            )

    # ==================================================
    # Render
    # ==================================================

    return render_template(
        "improvement/verification.html",
        improvement=improvement,
    )


# ==========================================================
# Approval
# ==========================================================

@improvement_bp.route(
    "/<int:improvement_id>/approve",
    methods=["POST"],
)
@login_required
def approve(improvement_id):

    # ==================================================
    # Get Improvement
    # ==================================================

    improvement = (
        improvement_service.get_by_id(
            improvement_id
        )
    )

    if not improvement:

        flash(
            "Improvement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "improvement.index"
            )
        )

    # ==================================================
    # Authorization
    # ==================================================

    if not authorization_service.can_approve_improvement(
        current_user,
        improvement,
    ):

        abort(403)

    # ==================================================
    # Get Employee ID
    # ==================================================

    approved_by_employee_id = (
        current_user.employee_id
    )

    if not approved_by_employee_id:

        flash(
            "Logged-in user is not linked "
            "to an employee.",
            "danger",
        )

        return redirect(
            url_for(
                "improvement.detail",
                improvement_id=improvement_id,
            )
        )

    # ==================================================
    # Approve
    # ==================================================

    try:

        improvement_service.approve_improvement(
            improvement_id=improvement_id,
            approved_by_employee_id=(
                approved_by_employee_id
            ),
        )

        flash(
            "Improvement approved. "
            "Problem has been closed.",
            "success",
        )

    except ValueError as e:

        flash(
            str(e),
            "danger",
        )

    except Exception:

        flash(
            "Failed to approve Improvement.",
            "danger",
        )

    # ==================================================
    # Return to Detail
    # ==================================================

    return redirect(
        url_for(
            "improvement.detail",
            improvement_id=improvement_id,
        )
    )


# ==========================================================
# Improvement Assignment / PIC
# ==========================================================

@improvement_bp.route(
    "/assign/<int:improvement_id>",
    methods=["GET"],
)
@login_required
def assign(improvement_id):

    # ==================================================
    # Get Improvement
    # ==================================================

    improvement = (
        improvement_service.get_by_id(
            improvement_id
        )
    )

    if not improvement:

        flash(
            "Improvement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "improvement.index"
            )
        )

    # ==================================================
    # Authorization
    # ==================================================

    if not authorization_service.can_assign_improvement(
        current_user,
        improvement,
    ):

        abort(403)

    # ==================================================
    # Get Related Problem
    # ==================================================

    problem = improvement.problem

    if not problem:

        flash(
            "Related problem not found.",
            "danger",
        )

        return redirect(
            url_for(
                "improvement.detail",
                improvement_id=improvement_id,
            )
        )

    # ==================================================
    # Get Improvement PIC
    # ==================================================

    improvement_pics = (
        improvement_service.get_pics(
            improvement_id
        )
    )

    # ==================================================
    # Get Owner
    # ==================================================

    owner = (
        improvement.owner_employee
        if improvement.owner_employee_id
        else None
    )

    # ==================================================
    # Render
    # ==================================================

    return render_template(
        "improvement/assignment.html",
        improvement=improvement,
        problem=problem,
        improvement_pics=improvement_pics,
        owner=owner,
    )

# ==========================================================
# Export Improvement PDF
# ==========================================================

@improvement_bp.route(
    "/<int:improvement_id>/pdf"
)
@login_required
def export_pdf(improvement_id):

    # ==================================================
    # Get Improvement
    # ==================================================

    improvement = (
        improvement_service.get_by_id(
            improvement_id
        )
    )

    if not improvement:

        flash(
            "Improvement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "improvement.index"
            )
        )

    # ==================================================
    # Created By
    # ==================================================

    created_by_name = "-"

    if improvement.created_by:

        creator = (
            Employee.query
            .filter_by(
                id=improvement.created_by
            )
            .first()
        )

        if creator:

            created_by_name = (
                creator.full_name
            )

    # ==================================================
    # Printed By
    # ==================================================

    printed_by = "-"

    if current_user.employee_id:

        current_employee = (
            Employee.query
            .filter_by(
                id=current_user.employee_id
            )
            .first()
        )

        if current_employee:

            printed_by = (
                current_employee.full_name
            )

    # ==================================================
    # Generate PDF
    # ==================================================

    pdf_file = (
        PDFReportService
        .generate_improvement_report(
            improvement=improvement,
            printed_by=printed_by,
            created_by_name=created_by_name,
        )
    )

    # ==================================================
    # Filename
    # ==================================================

    filename = (
        f"Improvement Report - "
        f"{improvement.improvement_no}.pdf"
    )

    # ==================================================
    # Return PDF
    # ==================================================

    return send_file(

        pdf_file,

        mimetype="application/pdf",

        as_attachment=False,

        download_name=filename,

    )