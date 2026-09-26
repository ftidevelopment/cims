from flask import (
    Blueprint,
    render_template,
    abort,
    request,
)

from app.services.public.public_problem_dashboard_service import (
    PublicProblemDashboardService,
)

from app.services.public.public_problem_list_service import (
    PublicProblemListService,
)

from app.services.problem_dashboard_service import (
    ProblemDashboardService,
)

from app.services.problem_attachment_service import (
    ProblemAttachmentService,
)


problem_dashboard_bp = Blueprint(
    "problem_dashboard",
    __name__,
    url_prefix="/problem-dashboard",
)


# =========================================================
# PUBLIC PROBLEM DASHBOARD
# =========================================================

@problem_dashboard_bp.route("/")
def index():

    service = PublicProblemDashboardService()

    dashboard = service.get_dashboard()

    return render_template(
        "problem_dashboard/index.html",
        dashboard=dashboard,
    )


# =========================================================
# PUBLIC PROBLEM LIST
# =========================================================

@problem_dashboard_bp.route("/problems")
def problems():

    # =====================================================
    # QUERY PARAMETERS
    # =====================================================

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

    search = request.args.get(
        "search",
        "",
        type=str,
    ).strip()

    status = request.args.get(
        "status",
        "",
        type=str,
    ).strip()

    priority = request.args.get(
        "priority",
        "",
        type=str,
    ).strip()

    department_id = request.args.get(
        "department_id",
        "",
        type=str,
    ).strip()

    open_only = (
        request.args.get(
            "open_only",
            "",
            type=str,
        ).lower()
        == "true"
    )

    period = request.args.get(
        "period",
        "",
        type=str,
    ).strip()

    aging = request.args.get(
        "aging",
        "",
        type=str,
    ).strip()

    # =====================================================
    # SERVICE
    # =====================================================

    service = PublicProblemListService()

    result = service.get_problems(
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        priority=priority,
        department_id=department_id,
        open_only=open_only,
        period=period,
        aging=aging,
    )

    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "problem_dashboard/problems.html",

        problems=result["problems"],

        pagination=result["pagination"],

        search=result["search"],

        status=result["status"],

        priority=result["priority"],

        department_id=result["department_id"],

        open_only=result["open_only"],

        period=result["period"],

        aging=result["aging"],

        period_start=result["period_start"],

        period_end=result["period_end"],
    )


# =========================================================
# PUBLIC PROBLEM DETAIL
# =========================================================

@problem_dashboard_bp.route(
    "/view/<int:problem_id>"
)
def view(problem_id):

    service = ProblemDashboardService()

    problem = service.get_problem_detail(
        problem_id
    )

    if not problem:
        abort(404)

    return render_template(
        "problem_dashboard/view.html",
        problem=problem,
    )


# =========================================================
# PUBLIC ATTACHMENT PREVIEW
# =========================================================

@problem_dashboard_bp.route(
    "/attachment/<int:attachment_id>/preview"
)
def attachment_preview(attachment_id):

    service = ProblemAttachmentService()

    return service.preview(
        attachment_id
    )


# =========================================================
# PUBLIC ATTACHMENT DOWNLOAD
# =========================================================

@problem_dashboard_bp.route(
    "/attachment/<int:attachment_id>/download"
)
def attachment_download(attachment_id):

    service = ProblemAttachmentService()

    return service.download(
        attachment_id
    )