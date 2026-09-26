from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)

from flask_login import (
    login_required,
    current_user,
)

from app.core.authorization import (
    permission_required,
)

from app.services.department_service import (
    DepartmentService,
)

from app.services.problem_category_service import (
    ProblemCategoryService,
)

from app.services.problem_service import (
    ProblemService,
)

from app.services.problem_assignment_service import (
    ProblemAssignmentService,
)

from app.services.employee_service import (
    EmployeeService,
)

from app.core.choices.problem import (
    PROBLEM_STATUS,
    ProblemStatus,
    PROBLEM_PRIORITY,
    PROBLEM_SOURCE,
)
from app.services.authorization_service import (
    AuthorizationService,
)

from app.services.pdf_report_service import (
    PDFReportService,
)


# ==========================================================
# Blueprint
# ==========================================================

problem_bp = Blueprint(
    "problem",
    __name__,
    url_prefix="/problems",
)


# ==========================================================
# Services
# ==========================================================

problem_service = ProblemService()

problem_assignment_service = (
    ProblemAssignmentService()
)

employee_service = (
    EmployeeService()
)

department_service = (
    DepartmentService()
)

problem_category_service = (
    ProblemCategoryService()
)
authorization_service = (
    AuthorizationService()
)

pdf_report_service = PDFReportService()

# ==========================================================
# LIST
# ==========================================================

@problem_bp.route("/")
@login_required
@permission_required("PROBLEM_VIEW")
def index():

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    keyword = request.args.get(
        "keyword",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "",
    )

    priority = request.args.get(
        "priority",
        "",
    )

    department_id = request.args.get(
        "department_id",
        None,
        type=int,
    )

    date_from = request.args.get(
        "date_from",
        "",
    ).strip()

    date_to = request.args.get(
        "date_to",
        "",
    ).strip()

    sort_by = request.args.get(
        "sort",
        "problem_no",
    )

    sort_order = request.args.get(
        "order",
        "desc",
    )

    # ==========================================
    # My Problems
    # ==========================================
    #
    # mine=1
    # berarti hanya menampilkan Problem
    # yang dibuat oleh user yang sedang login.
    #
    # Jika mine tidak ada, maka tampil semua Problem.
    # ==========================================

    mine = request.args.get(
        "mine",
        "",
    )

    created_by = None

    if mine == "1":

        created_by = current_user.id

    # ==========================================
    # Departments
    # ==========================================

    departments = department_service.get_all(
        page=1,
        per_page=1000,
        sort_by="department_name",
        sort_order="asc",
    )

    # ==========================================
    # Problems
    # ==========================================

    result = problem_service.get_all(
        keyword=keyword,
        status=status,
        priority=priority,
        department_id=department_id,
        date_from=date_from,
        date_to=date_to,
        created_by=created_by,
        page=page,
        per_page=10,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "problem/list.html",

        problems=result,

        keyword=keyword,

        status=status,

        priority=priority,

        department_id=department_id,

        departments=departments.items,

        date_from=date_from,

        date_to=date_to,

        sort_by=sort_by,

        sort_order=sort_order,

        mine=mine,

        PROBLEM_STATUS=PROBLEM_STATUS,

        ProblemStatus=ProblemStatus,

        PROBLEM_PRIORITY=PROBLEM_PRIORITY,
    )

# ==========================================================
# CREATE
# ==========================================================

@problem_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@permission_required("PROBLEM_CREATE")
def create():

    # ======================================================
    # POST
    # ======================================================

    if request.method == "POST":

        result = problem_service.create(

            form_data=request.form,

            files=request.files,

            reporter_employee_id=(
                current_user.employee_id
            ),

            created_by=current_user.id,
        )

        if result.success:

            flash(
                result.message,
                "success",
            )

            return redirect(
                url_for(
                    "problem.index"
                )
            )

        flash(
            result.message,
            "danger",
        )

    # ======================================================
    # Master Data
    # ======================================================

    departments = (
        department_service.get_all(
            per_page=1000,
        )
    )

    problem_categories = (
        problem_category_service.get_all(
            per_page=1000,
        )
    )

    # ======================================================
    # Render
    # ======================================================

    return render_template(
        "problem/form.html",

        problem=None,

        departments=departments.items,

        problem_categories=(
            problem_categories.items
        ),

        PROBLEM_STATUS=PROBLEM_STATUS,

        PROBLEM_PRIORITY=PROBLEM_PRIORITY,

        PROBLEM_SOURCE=PROBLEM_SOURCE,
    )


# ==========================================================
# SHOW / VIEW
# ==========================================================

@problem_bp.route("/<int:problem_id>")
@login_required
@permission_required("PROBLEM_VIEW")
def show(problem_id):

    problem = problem_service.get_by_id(
        problem_id
    )

    if not problem:

        flash(
            "Problem not found.",
            "danger",
        )

        return redirect(
            url_for("problem.index")
        )

    # ==========================================
    # Check Assign Authority
    # ==========================================

    can_assign_problem = (
        authorization_service
        .can_assign_problem(
            problem=problem,

            employee_id=(
                current_user.employee_id
            ),

            role_code=(
                current_user.role_code
            ),
        )
    )

    return render_template(
        "problem/view.html",

        problem=problem,

        can_assign_problem=(
            can_assign_problem
        ),
    )


# ==========================================================
# EXPORT PDF
# ==========================================================

@problem_bp.route(
    "/<int:problem_id>/export-pdf",
)
@login_required
@permission_required("PROBLEM_VIEW")
def export_pdf(problem_id):

    # ======================================================
    # Get Problem
    # ======================================================

    problem = problem_service.get_by_id(
        problem_id
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

    # ======================================================
    # Generate PDF
    # ======================================================

    pdf_file = (
        pdf_report_service
        .generate_problem_report(

            problem=problem,

            printed_by=(
                current_user.employee.full_name
                if getattr(
                    current_user,
                    "employee",
                    None
                )
                else current_user.username
            ),
        )
    )

    # ======================================================
    # Filename
    # ======================================================

    filename = (
        f"Problem_Report_"
        f"{problem.problem_no}.pdf"
    )

    # ======================================================
    # Return PDF
    # ======================================================

    return send_file(

        pdf_file,

        mimetype="application/pdf",

        as_attachment=False,

        download_name=filename,
    )

# ==========================================================
# EDIT
# ==========================================================

@problem_bp.route(
    "/edit/<int:problem_id>",
    methods=["GET", "POST"],
)
@login_required
@permission_required("PROBLEM_EDIT")
def edit(problem_id):

    # ======================================================
    # Get Problem
    # ======================================================

    problem = (
        problem_service.get_by_id(
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

    # ======================================================
    # Master Data
    # ======================================================

    departments = (
        department_service.get_all(
            per_page=1000,
        )
    )

    problem_categories = (
        problem_category_service.get_all(
            per_page=1000,
        )
    )

    # ======================================================
    # GET
    # ======================================================

    if request.method == "GET":

        return render_template(
            "problem/form.html",

            problem=problem,

            departments=departments.items,

            problem_categories=(
                problem_categories.items
            ),

            PROBLEM_STATUS=PROBLEM_STATUS,

            PROBLEM_PRIORITY=PROBLEM_PRIORITY,

            PROBLEM_SOURCE=PROBLEM_SOURCE,
        )

    # ======================================================
    # POST
    #
    # Ownership authorization is handled inside
    # ProblemService -> AuthorizationService
    # ======================================================

    result = problem_service.update(

        problem_id=problem_id,

        form_data=request.form,

        files=request.files,

        updated_by=current_user.id,

        current_employee_id=(
            current_user.employee_id
        ),

        current_role_code=(
            current_user.role_code
        ),
    )

    # ======================================================
    # Success
    # ======================================================

    if result.success:

        flash(
            result.message,
            "success",
        )

        return redirect(
            url_for(
                "problem.index"
            )
        )

    # ======================================================
    # Failed
    # ======================================================

    flash(
        result.message,
        "danger",
    )

    return render_template(
        "problem/form.html",

        problem=problem,

        departments=departments.items,

        problem_categories=(
            problem_categories.items
        ),

        PROBLEM_STATUS=PROBLEM_STATUS,

        PROBLEM_PRIORITY=PROBLEM_PRIORITY,

        PROBLEM_SOURCE=PROBLEM_SOURCE,
    )


# ==========================================================
# DELETE
# ==========================================================

@problem_bp.route(
    "/delete/<int:problem_id>",
    methods=["POST"],
)
@login_required
@permission_required("PROBLEM_DELETE")
def delete(problem_id):

    result = problem_service.delete(

        problem_id=problem_id,

        deleted_by=current_user.id,

        current_employee_id=(
            current_user.employee_id
        ),

        current_role_code=(
            current_user.role_code
        ),
    )

    flash(
        result.message,

        "success"
        if result.success
        else "danger",
    )

    return redirect(
        url_for(
            "problem.index"
        )
    )


# ==========================================================
# ASSIGN PIC
# ==========================================================

@problem_bp.route(
    "/assign/<int:problem_id>",
    methods=["GET", "POST"],
)
@login_required
@permission_required("PROBLEM_ASSIGN")
def assign(problem_id):

    # ==========================================
    # Get Problem
    # ==========================================

    problem = (
        problem_service.get_by_id(
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

    # ==========================================
    # Check Assignment Authority
    # ==========================================

    can_assign = (
        authorization_service
        .can_assign_problem(
            user=current_user,
            problem=problem,
        )
    )

    if not can_assign:

        flash(
            "You do not have authority to assign "
            "PIC for this Problem.",
            "danger",
        )

        return redirect(
            url_for(
                "problem.show",
                problem_id=problem_id,
            )
        )

    # ==========================================
    # Get Departments
    # ==========================================

    departments = (
        department_service.get_all(
            page=1,
            per_page=1000,
            sort_by="department_name",
            sort_order="asc",
        )
    )

    # ==========================================
    # Get Employees
    # ==========================================

    employees = (
        employee_service.get_all(
            page=1,
            per_page=1000,
            sort_by="full_name",
            sort_order="asc",
        )
    )

    # ==========================================
    # Existing PIC
    # ==========================================

    selected_employee_ids = [
        str(problem_pic.employee_id)
        for problem_pic
        in problem.problem_pics
    ]

    # ==========================================
    # POST
    # ==========================================

    if request.method == "POST":

        priority = request.form.get(
            "priority",
            "",
        ).strip()

        target_date = request.form.get(
            "target_date",
            "",
        ).strip()

        employee_ids = request.form.getlist(
            "employee_ids"
        )

        # ======================================
        # Assign Problem PIC
        # ======================================

        result = (
            problem_assignment_service.assign(
                problem_id=problem_id,
                priority=priority,
                employee_ids=employee_ids,
                target_date=target_date,
                assigned_by=current_user.id,
            )
        )

        if result.success:

            flash(
                result.message,
                "success",
            )

            return redirect(
                url_for(
                    "problem.show",
                    problem_id=problem_id,
                )
            )

        flash(
            result.message,
            "danger",
        )

    # ==========================================
    # Render
    # ==========================================

    return render_template(
        "problem/assignment.html",

        problem=problem,

        departments=(
            departments.items
        ),

        employees=(
            employees.items
        ),

        selected_employee_ids=(
            selected_employee_ids
        ),

        PROBLEM_PRIORITY=(
            PROBLEM_PRIORITY
        ),
    )